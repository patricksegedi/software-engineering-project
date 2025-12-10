import json
import os

from smarterspeaker.db import SessionLocal  # 너희 프로젝트에서 쓰는 세션 팩토리 (get_db 아님)
from smarterspeaker.models import SpeakerProfile

BASE_DIR = os.path.dirname(__file__)
USERS_JSON_PATH = os.path.join(BASE_DIR, "smarterspeaker", "users.JSON")  # 경로는 실제 위치에 맞게 수정

def main():
    # 1) JSON 읽기
    with open(USERS_JSON_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)  # { "daniel": {...}, "mom": {...} } 이런 구조일 거야

    db = SessionLocal()
    try:
        for username, info in users.items():
            meta_json = json.dumps(info, ensure_ascii=False)
            sp = SpeakerProfile(username=username, meta_json=meta_json)
            db.add(sp)
        db.commit()
        print("✅ users.JSON 내용이 speaker_profiles 테이블로 옮겨졌습니다.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
