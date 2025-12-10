from smarterspeaker.models import User, Zone, Device, UserVoiceProfile
import tempfile
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from smarterspeaker.models import User, Zone, Device  # SpeakerProfile 제거 (현재 미사용)
from smarterspeaker.db import DATABASE_URL  # DB URL

from .speaker.voice_recorder import VoiceRecorder
from .smarthome_client import control_device
from .speaker.audio_to_text import AudioToText
from .speaker.wake_word_activation import WakeWordActivation
from .speaker.speaker_verification import SpeakerVerifier
from .ai.gemini_ai import GeminiAI
from .ai.permission_manager import PermissionManager
from .config import THRESHOLD

from playsound import playsound
from dotenv import load_dotenv
from typing import Dict

import shutil
import json
import requests
import os

BASE_DIR = os.path.dirname(__file__)
VOICE_DB_DIR = os.path.join(BASE_DIR, "voices_from_db")

# 환경 변수 로드
load_dotenv()

# =========================================================
#  DB 연결 (SQLAlchemy)
# =========================================================

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """새 SQLAlchemy 세션을 반환. 호출한 쪽에서 db.close() 해줘야 함."""
    return SessionLocal()


# =========================================================
#  화자 인증용 사용자 정보 로드 (DB 기반)
# =========================================================

def load_speaker_users():
    """
    DB user_voice_profiles에서 음성 blob을 읽어와
    SpeakerVerifier.identify_speaker()가 기대하는 users 딕셔너리 형태로 변환한다.

    최종 반환 구조 예시 (email 기준):

    {
      "daniel@gmail.com": {
        "voice_dir": "voices_from_db/daniel_at_gmail_com"
      },
      ...
    }

    여기서 voice_dir는 smarterspeaker/ 기준의 **상대 경로**이다.
    SpeakerVerifier.identify_speaker() 쪽에서는 이 path를 받아
    그 폴더 안의 모든 wav 파일을 이용해 화자 인증을 수행한다.
    """

    # 🔥 1) 디렉토리 초기화: 예전에 남아 있던 유저 폴더들 제거
    voices_root = os.path.join(BASE_DIR, "voices_from_db")
    if os.path.exists(voices_root):
        shutil.rmtree(voices_root)
    os.makedirs(voices_root, exist_ok=True)

    # 🔥 2) DB에서 현재 등록된 voice profile만 다시 채움
    db = get_db()
    speakers = {}

    try:
        profiles = db.query(UserVoiceProfile).join(User).all()
        if not profiles:
            print("[WARN] No UserVoiceProfile rows found in DB.")
            return speakers

        for p in profiles:
            email = p.user.email

            # 이메일을 폴더명으로 쓸 수 있게 sanitize
            safe_name = (
                email.replace("@", "_at_")
                .replace(":", "_")
                .replace("/", "_")
            )
            user_folder = os.path.join(voices_root, safe_name)
            os.makedirs(user_folder, exist_ok=True)

            # 각 유저마다 폴더 안에 enroll.wav 로 음성 저장
            file_path = os.path.join(user_folder, "enroll.wav")
            with open(file_path, "wb") as f:
                f.write(p.voice_blob)

            # SpeakerVerifier가 기대하는 구조:
            # dict -> info.get("voice_dir") 로 경로를 읽음
            # 여기서는 BASE_DIR 기준 상대 경로를 넣어준다.
            rel_user_folder = os.path.relpath(user_folder, BASE_DIR)

            speakers[email] = {
                "voice_dir": rel_user_folder
            }

        print("[DEBUG] Loaded speaker users from DB:", list(speakers.keys()))
        return speakers
    finally:
        db.close()



# =========================================================
#  (선택) 디바이스 조회 / 상태 업데이트 헬퍼
# =========================================================

def load_devices_from_db():
    """필요 시 사용할 수 있는 디바이스 목록 조회 헬퍼(현재는 직접 사용 안 함)."""
    db = get_db()
    try:
        devices = db.query(Device).all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "type": d.type,
                "zone_id": d.zone_id,
                "status": d.status,
            }
            for d in devices
        ]
    finally:
        db.close()


def update_device_status_db(device_id: int, new_status: str):
    """
    device_id에 해당하는 디바이스의 status를 직접 DB에서 업데이트.
    """
    db = get_db()
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            print(f"❗ Device not found in DB: id={device_id}")
            return
        device.status = new_status
        db.commit()
        print(f"✅ Device updated in DB: id={device_id}, status={new_status}")
    except Exception as e:
        print("❗ Error updating device in DB:", e)
    finally:
        db.close()


# =========================================================
#  스마트홈 제어 관련 헬퍼 함수들
# =========================================================


def try_handle_smart_home(text: str) -> bool:
    """
    STT로 나온 전체 문장을 받아서
    - zone
    - device_type
    - action
    을 간단한 규칙으로 추출한 뒤,
    세 개가 다 결정되면 handle_device_command를 호출한다.

    처리했으면 True, 아니면 False 반환.
    """
    t = text.strip()
    t_lower = t.lower()

    zone = None
    device_type = None
    action = None

    # ===== 1) 존 추출 =====
    # 거실 / 침실
    if "거실" in t or "living room" in t_lower:
        zone = "Living"
    elif "침실" in t or "안방" in t or "bedroom" in t_lower:
        zone = "Bedroom"
    # 현관 / 문 / front door
    elif "현관" in t or "문" in t or "door" in t_lower or "front door" in t_lower:
        zone = "Entrance"   # DB에서 현관 문이 속한 존 이름에 맞춰서

    # ===== 2) 기기 타입 추출 =====
    if "불" in t or "전등" in t or "light" in t_lower:
        device_type = "light"
    elif "에어컨" in t or "aircon" in t_lower or "ac" in t_lower:
        device_type = "ac"
    elif "티비" in t or "tv" in t_lower:
        device_type = "tv"
    elif "문" in t or "door" in t_lower or "front door" in t_lower:
        device_type = "door"

    # ===== 3) 액션 추출 =====
    if "켜" in t or "on" in t_lower:
        action = "on"
    elif "꺼" in t or "off" in t_lower:
        action = "off"
    elif "잠가" in t or "lock" in t_lower:
        action = "lock"
    elif "열어" in t or "unlock" in t_lower or "open" in t_lower:
        action = "unlock"

    # ===== 4) 최소 조건 체크 =====
    if not (device_type and action):
        # 기기 타입이나 액션을 못 찾으면 스마트홈 명령이 아님
        return False

    # zone 이 빠진 경우 기본값 적용 (에어컨/문 같이 global 장치용)
    if zone is None:
        if device_type == "ac":
            zone = "Living"      # 기본 에어컨 존
        elif device_type == "door":
            zone = "Entrance"    # 기본 현관 문 존

    # 그래도 zone이 없으면 포기
    if zone is None:
        return False

    # ===== 5) 실제 제어 호출 =====
    print(f"[SMART_HOME] zone={zone}, type={device_type}, action={action}")
    handle_device_command(zone, device_type, action)

    return True

def handle_device_command(zone: str, device_type: str, action: str) -> None:
    """
    zone / device_type / action 값을 받아서
    실제로 FastAPI 서버에 /device-control 요청을 보내는 함수.
    """
    print(f"[SPEAKER] control request: zone={zone}, type={device_type}, action={action}")
    result = control_device(zone, device_type, action)
    print(f"[SPEAKER] control result: {result}")

# =========================================================
#  메인 / 커맨드 모드
# =========================================================

def main():
    # 🔹 DB 기반 화자 인증용 users 딕셔너리 로드
    speaker_users = load_speaker_users()
    if not speaker_users:
        print("[WARN] No speaker users loaded from DB. Voice authentication will always fail until a profile is registered.")

    # 🔹 SpeakerVerifier는 ECAPA 모델을 로드하므로 한 번만 생성해서 재사용
    speaker_verifier = SpeakerVerifier()

    # Initialize Gemini AI
    gemini = GeminiAI(api_key=os.getenv("GEMINI_API_KEY"))

    # Initialize permission manager
    permission_manager = PermissionManager()

    # Initialize AudioToText and VoiceRecorder objects once (important!)
    audio_processor = AudioToText()
    voice_recorder = VoiceRecorder()

    while True:
        # 1. Voice recording
        recorded_file = voice_recorder.record()
        wake = WakeWordActivation(audio_processor, "Hello")

        # 2. Wake word verification
        if wake.is_activated("voice_sample.wav"):
            # 3. Speaker authentication (DB 기반 users 사용)
            user = speaker_verifier.identify_speaker(
                recorded_file, speaker_users, THRESHOLD
            )

            if user is not None:
                # user 는 화자 인증 결과 (이메일) 이라고 가정
                user_email = user

                # 기본 display name 은 이메일 앞부분
                display_name = user_email.split("@")[0]

                # DB 에서 진짜 이름 가져오기 시도
                db = get_db()
                try:
                    db_user = db.query(User).filter(User.email == user_email).first()
                    if db_user and db_user.name:
                        display_name = db_user.name
                except Exception as e:
                    print(f"[WARN] Failed to load name for {user_email}: {e}")
                finally:
                    db.close()

                print(f"✅ Authentication successful: {user_email} ({display_name})")

                # 이름 기반 인사
                greeting = f"Hello {display_name}, what can I help you with today?"
                print(f"🤖 {greeting}")
                tts_speak(greeting)

                # Enter command mode (내부 로직은 여전히 이메일 기준)
                print(f"\n🎯 {display_name}'s AI Assistant Mode")
                command_mode(
                    user_email,
                    voice_recorder,
                    audio_processor,
                    gemini,
                    permission_manager,
                )
                break



def command_mode(user: str, voice_recorder, audio_processor, gemini, permission_manager):
    """Continuous command processing mode"""
    print("📋 Command examples: 'What's the weather?', 'Play music', 'Turn on lights', etc.")

    while True:
        try:
            print("\n" + "=" * 50)
            print("💬 Please speak your command")
            print("⌨️  Press Enter to start recording")
            print("🚪 Type 'q' + Enter to logout")
            print("=" * 50)

            user_input = input(">>> ").strip().lower()
            if user_input == 'q':
                print(f"👋 {user} logged out.")
                break

            # Record command
            print("🎤 Please speak your command...")
            command_file = voice_recorder.record("command.wav", duration=5)

            # Convert speech to text
            try:
                print("🔄 Converting speech to text...")
                command_text = audio_processor.transcribe(command_file)
                print(f"📝 Recognized command: {command_text}")
            except Exception as e:
                print(f"❌ Speech conversion error: {e}")
                continue

            # 🔹 1차로 스마트홈 명령인지 먼저 체크
            if try_handle_smart_home(command_text):
                # 스마트홈 제어를 이미 수행했으므로,
                # 영화 검색 / Gemini 처리로 내려가지 않고 다음 명령으로
                continue

            # 🔹 영화 검색 API 호출
            try:
                print("🌐 Sending recognized text to movie search API...")
                resp = requests.post(
                    "http://127.0.0.1:8000/voice-search",
                    json={"text": command_text, "user": user},  # 화자 이름도 같이 전송
                    timeout=1.5,
                )

                if resp.ok:
                    api_data = resp.json()
                    allowed = api_data.get("allowed", True)
                    reason = api_data.get("reason")

                    # 🔒 나이 제한 걸린 경우
                    if not allowed:
                        print("🚫 Movie blocked by age restriction:", reason)
                        if reason:
                            tts_speak(reason)
                        else:
                            tts_speak("Sorry, this movie is restricted due to your age.")
                        continue
                else:
                    print(f"⚠️ Movie API returned status {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Movie API connection error: {e}")
                # 여기서 바로 continue 해서 Gemini까지 안 넘김
                continue

            if not command_text.strip():
                print("❌ Command not recognized. Please try again.")
                continue

            # Process with Gemini AI
            try:
                print("🤖 Processing with Gemini AI...")
                result = gemini.process_command(user, command_text)
            except Exception as e:
                print(f"❌ AI processing error: {e}")
                continue

            # Permission check
            if result['action']:
                allowed, permission_message = permission_manager.check_permission(
                    user, result['intent'], result['entities'], command_text
                )

                if not allowed:
                    print(f"🚫 Permission denied: {permission_message}")
                    print("🔊 Playing audio response...")
                    tts_speak(permission_message)
                    continue

            # Display AI response
            print(f"🤖 AI Response: {result['response']}")
            print(f"🔍 Intent: {result['intent']}")
            print(f"📊 Entities: {result['entities']}")

            # TTS response
            print("🔊 Playing audio response...")
            tts_speak(result['response'])

            # Execute action (DB 기반 device 제어)
            if result['action']:
                execute_action(result['action'])

        except KeyboardInterrupt:
            print(f"\n👋 {user} logged out.")
            break


# =========================================================
#  액션 실행 / TTS / 세션 관련 함수들
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"   # FastAPI 서버 주소 (현재는 직접 DB 사용하지만 남겨둠)


def execute_action(action: Dict):
    """Execute AI generated action (DB 기반으로 디바이스 상태 갱신)"""

    # Step 1: action 형식 확인
    if action.get("type") != "device_control":
        print("❗ Unknown action type:", action)
        return

    device_id = action.get("device_id")
    operation = action.get("operation")   # "on" / "off" / "toggle"

    if device_id is None:
        print("❗ device_id not provided in action")
        return

    # Step 2: DB에서 해당 디바이스 로드
    db = get_db()
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            print("❗ Device not found in DB:", device_id)
            return

        current_status = device.status
        device_type = device.type

        # Step 3: 다음 상태 결정
        if operation == "toggle":
            if device_type == "door":
                next_status = "unlocked" if current_status == "locked" else "locked"
            else:
                next_status = "off" if current_status == "on" else "on"
        else:
            next_status = operation   # on/off/locked/unlocked

        # Step 4: DB에 상태 업데이트
        device.status = next_status
        db.commit()
        print(f"✅ Device updated (DB): id={device_id}, status={next_status}")
    except Exception as e:
        print("❗ Error updating device in DB:", e)
    finally:
        db.close()


def tts_speak(text: str):
    """Convert text to speech and play"""
    try:
        import pyttsx3
        engine = pyttsx3.init()

        # Force English voice selection
        voices = engine.getProperty('voices')

        # Select best English voice
        english_voice_found = False
        for voice in voices:
            if any(lang in voice.id.lower() for lang in ['en_us', 'en-us', 'english', 'alex', 'daniel', 'karen', 'samantha']):
                engine.setProperty('voice', voice.id)
                english_voice_found = True
                print(f"🎤 Using English voice: {voice.name}")
                break

        if not english_voice_found and voices:
            # Use first voice (usually English on most systems)
            engine.setProperty('voice', voices[0].id)
            print(f"🎤 Using default voice: {voices[0].name}")

        # Voice settings
        engine.setProperty('rate', 160)     # Speaking rate
        engine.setProperty('volume', 0.9)   # Volume

        # Voice output
        print(f"🎤 TTS (🇺🇸 EN): '{text}'")
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"❌ TTS error: {e}")
        print("💬 Text response: " + text)


def start_ai_session_with_components(user: str, audio_processor, voice_recorder):
    """Start AI session with pre-initialized components"""
    print(f"[DEBUG] Starting AI session with existing components for user: {user}")

    try:
        # Initialize Gemini AI
        print("[DEBUG] Initializing Gemini AI...")
        gemini = GeminiAI(api_key=os.getenv("GEMINI_API_KEY"))
        print("[DEBUG] Gemini AI initialized")

        # Initialize permission manager
        print("[DEBUG] Initializing permission manager...")
        permission_manager = PermissionManager()
        print("[DEBUG] Permission manager initialized")

        # Add personalized greeting with TTS
        greeting = f"Hello {user}, what can I help you with today?"
        print(f"🤖 {greeting}")
        tts_speak(greeting)

        # Enter command mode
        print(f"\n🎯 {user}'s AI Assistant Mode")
        command_mode(user, voice_recorder, audio_processor, gemini, permission_manager)
    except Exception as e:
        print(f"[ERROR] Exception in start_ai_session_with_components: {e}")
        import traceback
        traceback.print_exc()


def start_ai_session_with_existing_components(user: str, audio_processor=None, voice_recorder=None):
    """Start AI session for authenticated user with existing components"""
    print(f"[DEBUG] start_ai_session_with_existing_components called for user: {user}")

    try:
        # Initialize Gemini AI
        print("[DEBUG] Initializing Gemini AI...")
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"[DEBUG] API Key exists: {api_key is not None}")
        gemini = GeminiAI(api_key=api_key)
        print("[DEBUG] Gemini AI initialized")

        # Initialize permission manager
        print("[DEBUG] Initializing permission manager...")
        permission_manager = PermissionManager()
        print("[DEBUG] Permission manager initialized")

        # Use existing audio components or create new ones
        if audio_processor is None or voice_recorder is None:
            print("[DEBUG] Creating new audio components...")
            audio_processor = AudioToText()
            voice_recorder = VoiceRecorder()
            print("[DEBUG] Audio components created")
        else:
            print("[DEBUG] Using existing audio components")

        # Add personalized greeting with TTS
        greeting = f"Hello {user}, what can I help you with today?"
        print(f"🤖 {greeting}")
        print("[DEBUG] About to call tts_speak...")
        tts_speak(greeting)
        print("[DEBUG] TTS completed")

        # Enter command mode
        print(f"\n🎯 {user}'s AI Assistant Mode")
        print("[DEBUG] Entering command_mode...")
        command_mode(user, voice_recorder, audio_processor, gemini, permission_manager)
    except Exception as e:
        print(f"[ERROR] Exception in start_ai_session: {e}")
        import traceback
        traceback.print_exc()


def start_ai_session(user: str):
    """Start AI session for authenticated user"""
    print(f"[DEBUG] start_ai_session called for user: {user}")

    try:
        # Initialize Gemini AI
        print("[DEBUG] Initializing Gemini AI...")
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"[DEBUG] API Key exists: {api_key is not None}")
        gemini = GeminiAI(api_key=api_key)
        print("[DEBUG] Gemini AI initialized")

        # Initialize permission manager
        print("[DEBUG] Initializing permission manager...")
        permission_manager = PermissionManager()
        print("[DEBUG] Permission manager initialized")

        # Initialize VoiceRecorder only (AudioToText causes issues)
        print("[DEBUG] Initializing voice recorder...")
        voice_recorder = VoiceRecorder()
        print("[DEBUG] Voice recorder initialized")

        # Skip AudioToText initialization for now
        audio_processor = None
        print("[DEBUG] Skipping AudioToText initialization to avoid conflicts")

        # Add personalized greeting with TTS
        greeting = f"Hello {user}, what can I help you with today?"
        print(f"🤖 {greeting}")
        print("[DEBUG] About to call tts_speak...")
        tts_speak(greeting)
        print("[DEBUG] TTS completed")

        # Enter command mode
        print(f"\n🎯 {user}'s AI Assistant Mode")
        print("[DEBUG] Entering command_mode...")
        command_mode(user, voice_recorder, audio_processor, gemini, permission_manager)
    except Exception as e:
        print(f"[ERROR] Exception in start_ai_session: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
