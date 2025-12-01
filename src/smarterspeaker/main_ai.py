from .speaker.voice_recorder import VoiceRecorder
from .speaker.audio_to_text import AudioToText
from .speaker.wake_word_activation import WakeWordActivation
from .speaker.speaker_verification import SpeakerVerifier
from .ai.gemini_ai import GeminiAI
from .ai.permission_manager import PermissionManager
# from tts import tts_speak  # 기존 TTS 모듈은 나중에 설정
from playsound import playsound
from .config import THRESHOLD
import json
import os
from dotenv import load_dotenv
from typing import Dict

# 환경 변수 로드
load_dotenv()

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
                playsound(f"voice_samples/{user}/voices/valid.wav")
                
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
            
            # Execute action
            if result['action']:
                execute_action(result['action'])
            
        except KeyboardInterrupt:
            print(f"\n👋 {user} logged out.")
            break

def execute_action(action: Dict):
    """Execute AI generated action"""
    action_type = action.get('type')
    
    if action_type == 'device_control':
        print(f"🏠 Device control: {action}")
        # TODO: Add actual IoT device control code
        # Example: smart_home_api.control_device(action['device'], action['parameters'])
        
    elif action_type == 'weather_query':
        print(f"☁️ Weather query: {action}")
        # TODO: Add weather API call code
        # Example: weather_api.get_weather(action['time'])
        
    elif action_type == 'music_play':
        print(f"🎵 Music playback: {action}")
        # TODO: Add music streaming API call
        # Example: music_api.play(action['query'])

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