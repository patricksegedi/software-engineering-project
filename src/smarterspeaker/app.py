# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# === 1) 유저 + 영화 데이터 로드 ===
USERS_PATH = BASE_DIR / "src" / "smarterspeaker" / "users.JSON"
MOVIES_PATH = BASE_DIR / "src" / "smarterspeaker" / "movies.json"  # 네가 만든 movies.json 위치로 바꿔도 됨

with open(USERS_PATH, "r", encoding="utf-8") as f:
    USERS = json.load(f)

with open(MOVIES_PATH, "r", encoding="utf-8") as f:
    movies_data = json.load(f)
    # 너 movies.json 구조에 맞게 results / movies 등 가져오기
    MOVIES = movies_data.get("results", movies_data)

# 메모리 상태
VOICE_QUERY = {
    "query": None,
    "count": 0,
    "user": None,
    "allowed": True,
    "reason": None,
}


class VoiceSearchRequest(BaseModel):
    text: str
    user: str | None = None


def get_required_age(query: str) -> int:
    """
    query(음성에서 인식된 텍스트)가 가리키는 영화들의 나이 제한 중
    가장 높은 값(최소 요구 나이)을 계산.
    movies.json 안에 ageRating 값이 있어야 함.
    """
    q = query.lower()
    matched = [
        m for m in MOVIES
        if q in m.get("title", "").lower()
    ]

    if not matched:
        return 0  # 매칭이 없으면 제한 없음

    # ageRating 없으면 0으로 취급
    required = max(m.get("ageRating", 0) for m in matched)
    return required


@app.post("/voice-search")
def save_voice_search(data: VoiceSearchRequest):
    """
    AI 스피커가 { text, user }를 보내는 엔드포인트.
    여기서 나이 비교해서 allowed / reason을 결정한다.
    """
    global VOICE_QUERY

    query = (data.text or "").strip()
    user = data.user

    allowed = True
    reason = None

    user_age = None
    if user and user in USERS:
        info = USERS[user]
        # 새 users.JSON 구조: { "age": 15, "voice_dir": "..." }
        if isinstance(info, dict):
            user_age = info.get("age")

    # 유저 나이와 영화 나이제한 둘 다 있을 때만 비교
    if user_age is not None and query:
        required_age = get_required_age(query)
        if required_age > 0 and user_age < required_age:
            allowed = False
            reason = f"Age restricted: user_age={user_age}, required_age={required_age}"

    VOICE_QUERY = {
        "query": query,
        "count": VOICE_QUERY["count"] + 1,
        "user": user,
        "allowed": allowed,
        "reason": reason,
    }

    print(f"[API] Stored voice query='{query}', user={user}, allowed={allowed}, reason={reason}")

    return {"status": "ok", **VOICE_QUERY}


@app.get("/voice-search")
def get_voice_search():
    return VOICE_QUERY


@app.post("/voice-search/reset")
def reset_voice_search():
    global VOICE_QUERY
    VOICE_QUERY = {
        "query": None,
        "count": 0,
        "user": None,
        "allowed": True,
        "reason": None,
    }
    print("[API] Voice query reset")
    return {"status": "reset"}
