from .speaker.voice_recorder import VoiceRecorder
from .smarthome_client import control_device
from .speaker.audio_to_text import AudioToText
from .speaker.wake_word_activation import WakeWordActivation
from .speaker.speaker_verification import SpeakerVerifier
from .ai.gemini_ai import GeminiAI
from .ai.permission_manager import PermissionManager
# from tts import tts_speak  # 기존 TTS 모듈은 나중에 설정
from playsound import playsound
from .config import THRESHOLD
import json
import requests
import os
from dotenv import load_dotenv
from typing import Dict

BASE_DIR = os.path.dirname(__file__)

# 환경 변수 로드
load_dotenv()


# =========================================================
#  스마트홈 제어 관련 헬퍼 함수들
# =========================================================

def handle_device_command(zone: str, device_type: str, action: str) -> None:
    """
    zone / device_type / action 값을 받아서
    실제로 FastAPI 서버에 /device-control 요청을 보내는 함수.
    """
    print(f"[SPEAKER] control request: zone={zone}, type={device_type}, action={action}")
    result = control_device(zone, device_type, action)
    print(f"[SPEAKER] control result: {result}")


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
    if "거실" in t or "living room" in t_lower:
        zone = "Living"
    elif "침실" in t or "안방" in t or "bedroom" in t_lower:
        zone = "Bedroom"

    # ===== 2) 기기 타입 추출 =====
    if "불" in t or "전등" in t or "light" in t_lower:
        device_type = "light"
    elif "에어컨" in t or "aircon" in t_lower or "ac" in t_lower:
        device_type = "ac"
    elif "티비" in t or "tv" in t_lower:
        device_type = "tv"
    elif "문" in t or "door" in t_lower:
        device_type = "door"

    # ===== 3) 액션 추출 =====
    if "켜" in t or "on" in t_lower:
        action = "on"
    elif "꺼" in t or "off" in t_lower:
        action = "off"
    elif "잠가" in t or "lock" in t_lower:
        action = "lock"
    elif "열어" in t or "unlock" in t_lower:
        action = "unlock"

    # 세 개 다 못 찾으면 스마트홈 명령이 아닌 걸로 간주
    if not (zone and device_type and action):
        return False

    # ===== 4) 실제 제어 호출 =====
    print(f"[SMART_HOME] zone={zone}, type={device_type}, action={action}")
    handle_device_command(zone, device_type, action)

    return True


# =========================================================
#  메인 / 커맨드 모드
# =========================================================

def main():
    # Initialize Gemini AI
    gemini = GeminiAI(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Initialize permission manager
    permission_manager = PermissionManager()
    
    # Initialize AudioToText and VoiceRecorder objects once (important!)
    audio_processor = AudioToText()
    voice_recorder = VoiceRecorder()
    
    with open("src/smarterspeaker/users.JSON", "r") as file:
        users = json.load(file)
    
    while True:
        # 1. Voice recording
        recorded_file = voice_recorder.record()
        wake = WakeWordActivation(audio_processor, "Hello")
        
        # 2. Wake word verification
        if wake.is_activated("voice_sample.wav"):
            # 3. Speaker authentication
            user = SpeakerVerifier().identify_speaker(recorded_file, users, THRESHOLD)
            
            if user is not None:
                print(f"✅ Authentication successful: {user}")
                # Play welcome sound
                
                # Add personalized greeting with TTS
                greeting = f"Hello {user}, what can I help you with today?"
                print(f"🤖 {greeting}")
                tts_speak(greeting)
                
                # Enter command mode
                print(f"\n🎯 {user}'s AI Assistant Mode")
                command_mode(user, voice_recorder, audio_processor, gemini, permission_manager)
                break  # Exit loop when command mode ends
                    
            else:
                print("❌ Authentication failed!")
                playsound("src/smarterspeaker/voices/invalid.mp3")


def command_mode(user: str, voice_recorder, audio_processor, gemini, permission_manager):
    """Continuous command processing mode"""
    print("📋 Command examples: 'What's the weather?', 'Play music', 'Turn on lights', etc.")
    
    while True:
        try:
            print("\n" + "="*50)
            print("💬 Please speak your command")
            print("⌨️  Press Enter to start recording")
            print("🚪 Type 'q' + Enter to logout")
            print("="*50)
            
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

            # 🔹 기존 영화 검색 API 호출
            try:
                print("🌐 Sending recognized text to movie search API...")
                resp = requests.post(
                    "http://127.0.0.1:8000/voice-search",
                    json={"text": command_text, "user": user},  # 🔹 화자 이름도 같이 전송
                    timeout=1.5,
                )

                if resp.ok:
                    api_data = resp.json()
                    allowed = api_data.get("allowed", True)
                    reason = api_data.get("reason")

                    # 🔒 나이 제한 걸린 경우: 스피커가 reason 읽어주고, 다음 명령으로 넘어감
                    if not allowed:
                        print("🚫 Movie blocked by age restriction:", reason)
                        if reason:
                            tts_speak(reason)
                        else:
                            tts_speak("Sorry, this movie is restricted due to your age.")
                        # 이 명령은 여기서 끝. 아래 Gemini 처리로 내려가지 않음.
                        continue
                else:
                    print(f"⚠️ Movie API returned status {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Movie API connection error: {e}")
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
            
            # Execute action (기존 device_id 방식)
            if result['action']:
                execute_action(result['action'])
            
        except KeyboardInterrupt:
            print(f"\n👋 {user} logged out.")
            break


# =========================================================
#  기존 execute_action / TTS / 세션 관련 함수들
# =========================================================

BACKEND_URL = "http://127.0.0.1:8000"   # FastAPI 서버 주소

def execute_action(action: Dict):
    """Execute AI generated action"""

    # Step 1: action 형식 확인
    if action.get("type") != "device_control":
        print("❗ Unknown action type:", action)
        return

    device_id = action.get("device_id")
    operation = action.get("operation")   # "on" / "off" / "toggle"

    if device_id is None:
        print("❗ device_id not provided in action")
        return

    # Step 2: 현재 기기 상태 불러오기 (DB 기준으로 보고 싶으면 여기도 /devices-db 로 바꿀 수 있음)
    try:
        devices = requests.get(f"{BACKEND_URL}/devices-db").json()
    except Exception as e:
        print("❗ Could not load devices:", e)
        return

    dev_map = {d["id"]: d for d in devices}

    if device_id not in dev_map:
        print("❗ Device not found:", device_id)
        return

    current = dev_map[device_id]
    current_status = current["status"]

    # Step 3: 다음 상태 결정
    if operation == "toggle":
        if current["type"] == "door":
            next_status = "unlocked" if current_status == "locked" else "locked"
        else:
            next_status = "off" if current_status == "on" else "on"
    else:
        next_status = operation   # on/off/locked/unlocked

    # Step 4: 서버에 상태 업데이트 요청 👉 ✅ 여기만 핵심 변경
    try:
        res = requests.post(
            f"{BACKEND_URL}/devices-db/{device_id}",   # ✅ DB용 엔드포인트로 변경
            json={"status": next_status},
            timeout=3,
        )
        if res.status_code == 200:
            print(f"✅ Device updated (DB): id={device_id}, status={next_status}")
        else:
            print("❗ Update failed:", res.text)
    except Exception as e:
        print("❗ Error updating device:", e)


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
