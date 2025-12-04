# app.py (프로젝트 루트)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.smarterspeaker.db import engine
from src.smarterspeaker.models import Base
from src.smarterspeaker.api import router as sm_router  # api.py 안에 APIRouter

app = FastAPI(
    title="SmarterSpeaker API",
    version="0.1.0",
)

# CORS 설정 (개발 단계라 * 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 나중에 Vercel 도메인으로 변경 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 테이블 생성 (이미 있으면 무시)
Base.metadata.create_all(bind=engine)

# smarterspeaker.api 에서 정의한 모든 엔드포인트 등록
app.include_router(sm_router)
