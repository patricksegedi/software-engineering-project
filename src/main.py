# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 방금 그 api.py의 router 불러오기
from smarterspeaker.api import router as api_router

app = FastAPI(
    title="SmarterSpeaker JSON API",
    version="0.1.0",
)

# CORS: React(Vite)에서 호출할 수 있게 열어두기
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 나중에 필요하면 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 prefix 없이 그대로 붙이기 (React가 /users/... /devices... 로 부르니까)
app.include_router(api_router)

# (선택) python main.py로 바로 실행하고 싶을 때용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

