# src/smarterspeaker/api.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.utility.repositories.UserDboRepository import UserDboRepository
from fastapi import HTTPException
from pathlib import Path
import json
import shutil
from dotenv import load_dotenv
import os

from .movies import search_movies  # 상대 import (같은 패키지)

app = FastAPI(
    title="SmarterSpeaker Movie API",
    version="0.2.0",
)

# CORS: React에서 호출할 수 있게 허용 (개발 단계라 * 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 유저 정보 로드 (age 포함) ===
BASE_DIR = Path(__file__).resolve().parent  # src/smarterspeaker
USERS_PATH = BASE_DIR / "users.JSON"

with open(USERS_PATH, "r", encoding="utf-8") as f:
  USERS: Dict[str, Any] = json.load(f)

# ================================
# 1) 스마트홈 디바이스 상태 API
# ================================

class Device(BaseModel):
    id: int
    name: str
    type: str
    zone: str
    status: str  # "on" / "off" / "locked" / "unlocked"

# 웹 대시보드와 맞추기 위해 기본 디바이스를 이렇게 잡음
DEVICES: Dict[int, Device] = {
    1: Device(id=1, name="Living room lights", type="light", zone="Living Room", status="off"),
    2: Device(id=2, name="Living room TV",     type="tv",    zone="Living Room", status="off"),
    3: Device(id=3, name="Air conditioner",    type="ac",    zone="Living Room", status="off"),
    4: Device(id=4, name="Main door",          type="door",  zone="Entrance",    status="locked"),
    5: Device(id=5, name="Bedroom lights",     type="light", zone="Bedroom",     status="off"),
    6: Device(id=6, name="Kids room lights",   type="light", zone="Kids Room",   status="off"),
}

@app.get("/devices", response_model=List[Device])
def list_devices():
    """집 안 기기 전체 상태 조회 (웹 대시보드에서 사용)"""
    return list(DEVICES.values())


class DeviceUpdate(BaseModel):
    status: str  # "on" / "off" / "locked" / "unlocked"

@app.post("/devices/{device_id}", response_model=Device)
def update_device(device_id: int, payload: DeviceUpdate):
    """특정 기기 상태 변경 (웹/스피커 둘 다 여기로 요청)"""
    if device_id not in DEVICES:
        raise HTTPException(status_code=404, detail="Device not found")

    dev = DEVICES[device_id]
    dev.status = payload.status

    # 🔌 여기서 실제 IoT 제어 (라즈베리파이, MQTT 등) 붙이면 됨
    print(f"[IOT] {dev.name} -> {dev.status}")

    return dev

# ============================================
# 2) 회원가입 정보 → 스피커 쪽 유저로 등록 API
# ============================================

class UserRegisterRequest(BaseModel):
    name: str  # 스피커가 부를 이름 (예: "patrick")
    age: int   # 권한(미성년자 등)에 쓸 나이

@app.post("/users/register")
def register_user(body: UserRegisterRequest):
    """
    웹에서 회원가입할 때 스피커 유저 JSON(users.JSON)에 같이 저장
    """
    name = body.name

    if name in USERS:
        raise HTTPException(status_code=400, detail="User already exists")

    voice_dir = f"voice_samples/{name}"

    USERS[name] = {
        "age": body.age,
        "voice_dir": voice_dir,
    }

    # 폴더 생성
    voice_path = BASE_DIR / voice_dir
    voice_path.mkdir(parents=True, exist_ok=True)

    # JSON 파일에 다시 저장
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(USERS, f, ensure_ascii=False, indent=2)

    return {"name": name, "age": body.age, "voice_dir": voice_dir}


# ============================================
# 3) 웹에서 녹음한 음성 업로드 → 스피커에 저장
# ============================================

@app.post("/users/{name}/voice")
async def upload_voice_sample(name: str, file: UploadFile = File(...)):
    """
    웹에서 녹음한 음성을 업로드하면
    src/smarterspeaker/voice_samples/{name}/ 안에 저장
    """
    if name not in USERS:
        raise HTTPException(status_code=404, detail="Unknown user")

    voice_dir_rel = USERS[name]["voice_dir"]  # 예: "voice_samples/kun"
    voice_dir = BASE_DIR / voice_dir_rel
    voice_dir.mkdir(parents=True, exist_ok=True)

    dest_path = voice_dir / file.filename

    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"[VOICE] Saved sample for {name} at {dest_path}")
    return {"ok": True, "path": str(dest_path)}


class VoiceSearchRequest(BaseModel):
    text: str              # STT 결과 전체 문장
    user: Optional[str] = None  # 화자 이름 (예: "kun", "patrick")


class VoiceSearchResult(BaseModel):
    raw_text: str
    query: str
    count: int
    results: List[Dict[str, Any]]
    user: Optional[str] = None
    allowed: bool
    reason: Optional[str] = None

@app.get("/movies")
def get_movies(q: str = ""):
    """
    Search movies by title.
    - /movies          -> all movies
    - /movies?q=Inception -> movies whose title contains 'Inception'
    """
    results = search_movies(q)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


def extract_query_from_text(text: str) -> str:
    """
    Very simple rule-based extractor.
    e.g. "search Inception", "play the movie Interstellar"
    -> "Inception", "Interstellar"
    """
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
    """users.JSON에서 age 가져오기"""
    if not username:
        return None

    info = USERS.get(username)
    if isinstance(info, dict):
        return info.get("age")
    # 예전 구조(문자열 path만 있는 경우)면 age 없음
    return None


def get_required_age(results: List[Dict[str, Any]]) -> int:
    """검색된 영화들 중 가장 높은 ageRating 반환"""
    if not results:
        return 0
    return max(m.get("ageRating", 0) for m in results)


# 마지막 음성 검색 결과를 메모리에 저장할 전역 변수
_last_voice_search: Dict[str, Any] = {
    "raw_text": "",
    "query": "",
    "count": 0,
    "results": [],
    "user": None,
    "allowed": True,
    "reason": None,
}


@app.post("/voice-search", response_model=VoiceSearchResult)
def voice_search(payload: VoiceSearchRequest):
    """
    음성 인식(STT) 결과 문장을 받아서, 영화 검색을 수행.
    - body: {"text": "search Inception", "user": "kun"}
    """
    global _last_voice_search

    raw_text = (payload.text or "").strip()
    user = payload.user
    query = extract_query_from_text(raw_text)
    results = search_movies(query)

    # --- 연령 제한 계산 ---
    user_age = get_user_age(user)
    required_age = get_required_age(results)

    allowed = True
    reason: Optional[str] = None

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


@app.get("/voice-search", response_model=VoiceSearchResult)
def get_last_voice_search():
    """
    마지막으로 수행된 음성 영화 검색 결과를 반환.
    React에서 폴링하거나, 디버깅용으로 사용할 수 있음.
    """
    return _last_voice_search

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    restriction_list: Optional[int] = None

@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """
    Login using email + password.
    This checks the MySQL user using UserDboRepository.
    """
    repo = get_user_repo()

    try:
        user = repo.getUserByEmail(payload.email)
    finally:
        repo.close()

    # Invalid email or wrong password
    if not user or user.password != payload.password:
        return LoginResponse(
            success=False,
            message="Invalid email or password"
        )

    # Successful login
    return LoginResponse(
        success=True,
        message="Login successful",
        name=user.name,
        role=user.role,
        email=user.email,
        restriction_list=user.restriction_list,
    )


def get_user_repo():
    load_dotenv()

    return UserDboRepository(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=os.getenv("DB_PORT")
    )


