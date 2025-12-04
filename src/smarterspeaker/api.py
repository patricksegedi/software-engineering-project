# src/smarterspeaker/api.py
from sqlalchemy import or_
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pathlib import Path
import json
import shutil

# DB 관련 import
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .db import get_db
from . import models, schemas
from .movies import search_movies  # 영화 검색 모듈

# -------------------------------------------
# 라우터 생성 (여기서는 FastAPI 앱을 만들지 않는다)
# -------------------------------------------
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------
# 기존 JSON 기반 유저 데이터 로드 (영화 검색용)
# -------------------------------------------
BASE_DIR = Path(__file__).resolve().parent  # src/smarterspeaker
USERS_PATH = BASE_DIR / "users.JSON"

with open(USERS_PATH, "r", encoding="utf-8") as f:
    USERS: Dict[str, Any] = json.load(f)

# =======================================================
# 1) 기존: 스마트홈 디바이스 상태 API (in-memory)
# =======================================================

class Device(BaseModel):
    id: int
    name: str
    type: str
    zone: str
    status: str


DEVICES: Dict[int, Device] = {
    1: Device(id=1, name="Living room lights", type="light", zone="Living Room", status="off"),
    2: Device(id=2, name="Living room TV",     type="tv",    zone="Living Room", status="off"),
    3: Device(id=3, name="Air conditioner",    type="ac",    zone="Living Room", status="off"),
    4: Device(id=4, name="Main door",          type="door",  zone="Entrance",    status="locked"),
    5: Device(id=5, name="Bedroom lights",     type="light", zone="Bedroom",     status="off"),
    6: Device(id=6, name="Kids room lights",   type="light", zone="Kids Room",   status="off"),
}

@router.get("/devices", response_model=List[Device])
def list_devices():
    return list(DEVICES.values())


class DeviceUpdate(BaseModel):
    status: str


@router.post("/devices/{device_id}", response_model=Device)
def update_device(device_id: int, payload: DeviceUpdate):
    if device_id not in DEVICES:
        raise HTTPException(status_code=404, detail="Device not found")

    dev = DEVICES[device_id]
    dev.status = payload.status

    print(f"[IOT] {dev.name} -> {dev.status}")
    return dev


# =======================================================
# 2) 기존: 회원가입 정보를 users.JSON에 저장
# =======================================================

class UserRegisterRequest(BaseModel):
    name: str
    age: int


@router.post("/users/register")
def register_user(body: UserRegisterRequest):
    name = body.name

    if name in USERS:
        raise HTTPException(status_code=400, detail="User already exists")

    voice_dir = f"voice_samples/{name}"

    USERS[name] = {
        "age": body.age,
        "voice_dir": voice_dir,
    }

    (BASE_DIR / voice_dir).mkdir(parents=True, exist_ok=True)

    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(USERS, f, ensure_ascii=False, indent=2)

    return {"name": name, "age": body.age, "voice_dir": voice_dir}


# =======================================================
# 3) 기존: 웹에서 녹음 파일 업로드
# =======================================================

@router.post("/users/{name}/voice")
async def upload_voice_sample(name: str, file: UploadFile = File(...)):
    if name not in USERS:
        raise HTTPException(status_code=404, detail="Unknown user")

    voice_dir_rel = USERS[name]["voice_dir"]
    voice_dir = BASE_DIR / voice_dir_rel
    voice_dir.mkdir(parents=True, exist_ok=True)

    dest_path = voice_dir / file.filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"[VOICE] Saved sample for {name} at {dest_path}")
    return {"ok": True, "path": str(dest_path)}


# =======================================================
# 4) 기존: 영화 검색 기능
# =======================================================

class VoiceSearchRequest(BaseModel):
    text: str
    user: Optional[str] = None


class VoiceSearchResult(BaseModel):
    raw_text: str
    query: str
    count: int
    results: List[Dict[str, Any]]
    user: Optional[str]
    allowed: bool
    reason: Optional[str]


@router.get("/movies")
def get_movies(q: str = ""):
    results = search_movies(q)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


def extract_query_from_text(text: str) -> str:
    t = text.strip()
    if not t:
        return ""

    lowered = t.lower()

    prefixes = [
        "search",
        "find",
        "play",
        "play the movie",
        "play movie",
        "movie",
        "영화 찾아줘",
        "영화 틀어줘",
    ]

    for prefix in prefixes:
        if lowered.startswith(prefix):
            return t[len(prefix):].strip(" ,")

    return t


def get_user_age(username: Optional[str]) -> Optional[int]:
    info = USERS.get(username)
    if isinstance(info, dict):
        return info.get("age")
    return None


def get_required_age(results: List[Dict[str, Any]]) -> int:
    if not results:
        return 0
    return max(m.get("ageRating", 0) for m in results)


_last_voice_search: Dict[str, Any] = {
    "raw_text": "",
    "query": "",
    "count": 0,
    "results": [],
    "user": None,
    "allowed": True,
    "reason": None,
}


@router.post("/voice-search", response_model=VoiceSearchResult)
def voice_search(payload: VoiceSearchRequest):
    global _last_voice_search

    raw_text = (payload.text or "").strip()
    user = payload.user
    query = extract_query_from_text(raw_text)
    results = search_movies(query)

    user_age = get_user_age(user)
    required_age = get_required_age(results)

    allowed = True
    reason = None

    if user_age is not None and required_age > 0 and user_age < required_age:
        allowed = False
        reason = f"Age restricted: user_age={user_age}, required_age={required_age}"

    _last_voice_search = {
        "raw_text": raw_text,
        "query": query,
        "count": len(results),
        "results": results,
        "user": user,
        "allowed": allowed,
        "reason": reason,
    }
    return _last_voice_search


@router.get("/voice-search", response_model=VoiceSearchResult)
def get_last_voice_search():
    return _last_voice_search


# =======================================================
# 5) ⭐ 새로 추가된 DB 기반 API
# =======================================================

# ------------------------------
# 회원가입 (DB 기반)
# ------------------------------
@router.post("/auth/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(user_in.password)
    user = models.User(
        email=user_in.email,
        hashed_password=hashed_pw,
        age=user_in.age,
        family_role=user_in.family_role,
        is_admin=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ------------------------------
# Zones
# ------------------------------
@router.get("/zones", response_model=List[schemas.ZoneOut])
def list_zones(db: Session = Depends(get_db)):
    return db.query(models.Zone).order_by(models.Zone.order_index).all()


@router.post("/zones", response_model=schemas.ZoneOut)
def create_zone(zone_in: schemas.ZoneCreate, db: Session = Depends(get_db)):
    zone = models.Zone(**zone_in.dict())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


# ------------------------------
# Devices (DB 기반)
# ------------------------------
@router.get("/devices-db", response_model=List[schemas.DeviceOut])
def list_devices_db(db: Session = Depends(get_db)):
    return db.query(models.Device).all()


@router.post("/devices-db", response_model=schemas.DeviceOut)
def create_device(device_in: schemas.DeviceCreate, db: Session = Depends(get_db)):
    h = models.Device(**device_in.dict())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@router.post("/devices-db/{device_id}", response_model=schemas.DeviceOut)
def update_device_db(device_id: int, update: schemas.DeviceUpdate, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if update.status:
        device.status = update.status

    db.commit()
    db.refresh(device)
    return device

# ==========================================
# 8) Device Control (AI 스피커 → DB 제어)
# ==========================================

class DeviceControlRequest(BaseModel):
    zone: Optional[str] = None          # 예: "Living Room"
    device_type: Optional[str] = None   # 예: "light", "tv", "ac", "door"
    action: str                         # 예: "on", "off", "lock", "unlock"


@router.post("/device-control", response_model=List[schemas.DeviceOut])
def device_control(cmd: DeviceControlRequest, db: Session = Depends(get_db)):
    """
    AI 스피커가 자연어를 해석해서,
    zone + device_type + action 형태로 보내주면
    해당 존의 해당 타입 기기들을 DB에서 찾아 상태를 변경.
    """

    # 1) 기본 쿼리: Device + Zone join
    query = db.query(models.Device).join(models.Zone)

    # 2) zone 필터 (name 또는 display_name 에 포함되면 매칭)
    if cmd.zone:
        zone_like = f"%{cmd.zone}%"
        query = query.filter(
            or_(
                models.Zone.name.ilike(zone_like),
                models.Zone.display_name.ilike(zone_like),
            )
        )

    # 3) device_type 필터
    if cmd.device_type:
        query = query.filter(models.Device.type == cmd.device_type)

    devices = query.all()
    if not devices:
        raise HTTPException(status_code=404, detail="No matching devices found")

    # 4) action -> status 매핑
    action = cmd.action.lower()

    def map_status(device_type: str, action: str) -> str:
        if device_type in ["light", "tv", "ac"]:
            if action in ["on", "turn_on", "켜", "켜줘"]:
                return "on"
            if action in ["off", "turn_off", "꺼", "꺼줘"]:
                return "off"
        if device_type == "door":
            if action in ["lock", "잠가", "잠가줘"]:
                return "locked"
            if action in ["unlock", "열어", "열어줘"]:
                return "unlocked"
        # 기본값: 그냥 action 그대로 넣거나 기존 유지
        return action

    # 5) 각 디바이스 상태 업데이트
    for dev in devices:
        new_status = map_status(dev.type, action)
        dev.status = new_status

    db.commit()

    # 6) 갱신된 상태 다시 읽어서 반환
    for dev in devices:
        db.refresh(dev)

    return devices
