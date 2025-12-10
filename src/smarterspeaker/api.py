# src/smarterspeaker/api.py
from sqlalchemy import or_
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Depends, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .config import MASTER_KEY   

from io import BytesIO
from pydub import AudioSegment
from .db import DATABASE_URL
from .db import get_db
from . import models, schemas
from .movies import search_movies  # 영화 검색 모듈

import json

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)
MAX_PASSWORD_LEN = 72

app = FastAPI()
router = APIRouter()

VOICE_DIR = Path(__file__).resolve().parent / "voices"
VOICE_DIR.mkdir(exist_ok=True)

BASE_DIR = Path(__file__).resolve().parent

# =======================================================
# 1) (구현 그대로 사용) 인메모리 디바이스 API
#    -> 프론트에서 이걸 안 써도 상관 없음
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


@router.get("/debug/db")
def debug_db():
    return {"DATABASE_URL": DATABASE_URL}


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
# 2) 프로필 음성 업로드 (DB: user_voice_profiles.voice_blob 사용)
# =======================================================

@router.post("/users/{user_id}/voice-profile")
async def upload_voice_profile(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    프로필 페이지에서 업로드한 음성을 DB BLOB으로 저장.
    - 프론트에서 audio/webm 으로 올라오면 webm -> wav 로 변환해서 저장
    - 이미 wav 인 경우에는 그대로 저장
    """

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    content_type = file.content_type or ""

    try:
        # 🔥 1) webm 으로 올라온 경우: pydub + ffmpeg 로 wav 변환
        if "webm" in content_type or file.filename.endswith(".webm"):
            buf = BytesIO(raw)
            audio = AudioSegment.from_file(buf, format="webm")

            audio = audio.set_channels(1).set_frame_rate(16000)
            
            wav_io = BytesIO()
            audio.export(wav_io, format="wav")
            wav_bytes = wav_io.getvalue()
        else:
            # 🔥 2) 이미 wav 로 올라온 경우: 그대로 저장
            wav_bytes = raw

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode audio: {e}",
        )

    profile = (
        db.query(models.UserVoiceProfile)
        .filter(models.UserVoiceProfile.user_id == user_id)
        .first()
    )

    if profile is None:
        profile = models.UserVoiceProfile(user_id=user_id, voice_blob=wav_bytes)
        db.add(profile)
    else:
        profile.voice_blob = wav_bytes

    db.commit()
    return {"message": "Voice profile saved", "user_id": user_id}

# =======================================================
# 3) 영화 검색 + 나이 제한 (이제 JSON 말고 DB 기반)
# =======================================================

class VoiceSearchRequest(BaseModel):
    text: str
    # main_ai.py 에서 email 문자열을 넘겨주고 있으므로
    # 여기서도 user = 이메일 로 취급
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


def get_user_age_from_db(email: Optional[str], db: Session) -> Optional[int]:
    if not email:
        return None
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    return user.age


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
def voice_search(payload: VoiceSearchRequest, db: Session = Depends(get_db)):
    """
    main_ai.py 에서 인식된 자연어 명령(text)과 화자 email(user)을 받아
    영화 검색 + 나이 제한 체크를 수행.
    """
    global _last_voice_search

    raw_text = (payload.text or "").strip()
    user = payload.user
    query = extract_query_from_text(raw_text)
    results = search_movies(query)

    user_age = get_user_age_from_db(user, db)
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
# 4) 회원가입 / 로그인 / 유저 관리 (DB 기반)
# =======================================================

@router.post("/auth/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # 비밀번호 길이 체크
    if user_in.password and len(user_in.password.encode("utf-8")) > MAX_PASSWORD_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"Password too long (max {MAX_PASSWORD_LEN} bytes).",
        )

    # 이메일 중복 확인
    exists = db.query(models.User).filter(models.User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ 마스터키 기반 admin 여부 결정
    # - 비어 있으면 None 또는 "" → False
    # - MASTER_KEY와 같으면 True
    is_admin = bool(user_in.master_key and user_in.master_key == MASTER_KEY)

    hashed_pw = pwd_context.hash(user_in.password)

    user = models.User(
        email=user_in.email,
        name=user_in.name,                   # ✅ 이름 저장
        hashed_password=hashed_pw,
        age=user_in.age,
        family_role=user_in.family_role,
        is_admin=is_admin,                   # ✅ admin 여부 반영
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    """
    전체 사용자 목록 조회 (관리자 페이지용)
    """
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    return users


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 삭제 (관리자 페이지에서 계정 지울 때 사용)
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return Response(status_code=204)


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/auth/login", response_model=schemas.UserOut)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    """
    이메일 + 비밀번호 로그인.
    해시 검증은 passlib CryptContext 사용 (pbkdf2_sha256 / bcrypt 둘 다 지원).
    """
    if login_req.password and len(login_req.password.encode("utf-8")) > MAX_PASSWORD_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"Password too long (max {MAX_PASSWORD_LEN} bytes).",
        )

    user = db.query(models.User).filter(models.User.email == login_req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not pwd_context.verify(login_req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return user


# =======================================================
# 5) Zones (DB)
# =======================================================

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


@router.delete("/zones/{zone_id}", status_code=204)
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # 해당 존에 속한 디바이스들도 같이 삭제
    db.query(models.Device).filter(models.Device.zone_id == zone_id).delete()

    db.delete(zone)
    db.commit()
    return Response(status_code=204)


# =======================================================
# 6) Devices (DB)
# =======================================================

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


@router.delete("/devices-db/{device_id}", status_code=204)
def delete_device_db(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    db.delete(device)
    db.commit()
    return Response(status_code=204)


# =======================================================
# 7) Device Control (AI 스피커 → DB 상태 제어)
# =======================================================

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

    query = db.query(models.Device).join(models.Zone)

    if cmd.zone:
        zone_like = f"%{cmd.zone}%"
        query = query.filter(
            or_(
                models.Zone.name.ilike(zone_like),
                models.Zone.display_name.ilike(zone_like),
            )
        )

    if cmd.device_type:
        query = query.filter(models.Device.type == cmd.device_type)

    devices = query.all()
    if not devices:
        raise HTTPException(status_code=404, detail="No matching devices found")

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
        return action

    for dev in devices:
        new_status = map_status(dev.type, action)
        dev.status = new_status

    db.commit()

    for dev in devices:
        db.refresh(dev)

    return devices

app.include_router(router)