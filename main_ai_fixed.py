from voice_recorder import VoiceRecorder
from audio_to_text import AudioToText
from wake_word_activation import WakeWordActivation
from speaker_verification import SpeakerVerifier
from gemini_ai import GeminiAI
from permission_manager import PermissionManager
from playsound import playsound
from config import THRESHOLD
import json
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# 환경 변수 로드
load_dotenv()

class SmartSpeaker:
    def __init__(self):
        """스마트 스피커 초기화"""
        print("🤖 스마트 스피커 시스템 시작")
        
        # 모든 객체를 한 번만 생성
        self.audio_processor = AudioToText()
        self.gemini = GeminiAI(api_key=os.getenv("GEMINI_API_KEY"))
        self.permission_manager = PermissionManager()
        self.voice_recorder = VoiceRecorder()
        self.speaker_verifier = SpeakerVerifier()
        
        # 사용자 데이터 로드
        with open("users.json", "r") as file:
            self.users = json.load(file)
        
        print("✅ 초기화 완료!")

    def authenticate_user(self) -> Optional[str]:
        """사용자 인증 단계"""
        print("\n🔐 === 사용자 인증 단계 ===")
        
        while True:
            print("🎙️ 'Hello'라고 말해서 시스템을 활성화하세요...")
            
            # 1. 음성 녹음
            recorded_file = self.voice_recorder.record()
            
            # 2. 웨이크워드 확인
            wake = WakeWordActivation(self.audio_processor, "Hello")
            if not wake.is_activated("voice_sample.wav"):
                print("❌ 웨이크워드가 인식되지 않았습니다. 다시 시도해주세요.")
                continue
            
            print("✅ 웨이크워드 확인됨")
            
            # 3. 화자 인증
            user = self.speaker_verifier.identify_speaker(recorded_file, self.users, THRESHOLD)
            
            if user is not None:
                print(f"✅ 인증 성공: {user}")
                playsound(f"voice_samples/{user}/voices/valid.wav")
                return user
            else:
                print("❌ 화자 인증 실패! 등록된 사용자가 아닙니다.")
                playsound("voices/invalid.mp3")
                
                # 재시도 여부 묻기
                retry = input("다시 시도하시겠습니까? (y/n): ").lower()
                if retry != 'y':
                    return None

    def process_commands(self, user: str):
        """명령 처리 단계"""
        print(f"\n🎤 === {user}님의 AI 어시스턴트 ===")
        
        while True:
            try:
                # 1. 명령 녹음
                print(f"\n{user}님, 명령을 말씀하세요... (종료하려면 'quit' 또는 Ctrl+C)")
                command_file = self.voice_recorder.record("command.wav", duration=5)
                
                # 2. 음성을 텍스트로 변환
                print("🔄 음성을 텍스트로 변환 중...")
                command_text = self.audio_processor.transcribe(command_file)
                
                if not command_text.strip():
                    print("❌ 명령을 인식하지 못했습니다. 다시 시도해주세요.")
                    continue
                
                print(f"📝 인식된 명령: '{command_text}'")
                
                # 종료 명령 확인
                if any(word in command_text.lower() for word in ['quit', 'exit', '종료', '그만']):
                    print("👋 AI 어시스턴트를 종료합니다.")
                    break
                
                # 3. AI 처리
                print("🤖 Gemini AI 처리 중...")
                result = self.gemini.process_command(user, command_text)
                
                # 4. 권한 검사
                if result['action']:
                    allowed, permission_message = self.permission_manager.check_permission(
                        user, result['intent'], result['entities']
                    )
                    
                    if not allowed:
                        print(f"🚫 권한 거부: {permission_message}")
                        self.tts_speak(permission_message)
                        continue
                
                # 5. 결과 출력
                print(f"🤖 AI 응답: {result['response']}")
                print(f"🔍 의도: {result['intent']}")
                print(f"📊 정보: {result['entities']}")
                
                # 6. TTS 응답
                self.tts_speak(result['response'])
                
                # 7. 액션 실행
                if result['action']:
                    self.execute_action(result['action'])
                
            except KeyboardInterrupt:
                print("\n👋 사용자가 종료했습니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                print("다시 시도해주세요.")

    def execute_action(self, action: Dict):
        """액션 실행"""
        action_type = action.get('type')
        
        if action_type == 'device_control':
            print(f"🏠 기기 제어: {action}")
        elif action_type == 'weather_query':
            print(f"☁️ 날씨 조회: {action}")
        elif action_type == 'music_play':
            print(f"🎵 음악 재생: {action}")

    def tts_speak(self, text: str):
        """TTS 음성 출력"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.say(text)
            engine.runAndWait()
        except:
            print("🔇 TTS 음성 출력을 사용할 수 없습니다.")

    def run(self):
        """메인 실행 루프"""
        print("🎯 스마트 스피커가 준비되었습니다!")
        
        while True:
            try:
                # 1. 사용자 인증
                user = self.authenticate_user()
                if user is None:
                    print("👋 시스템을 종료합니다.")
                    break
                
                # 2. 명령 처리
                self.process_commands(user)
                
                # 3. 로그아웃 후 재시작
                print(f"\n{user}님이 로그아웃했습니다.")
                
            except KeyboardInterrupt:
                print("\n👋 시스템을 종료합니다.")
                break

def main():
    speaker = SmartSpeaker()
    speaker.run()

if __name__ == "__main__":
    main()