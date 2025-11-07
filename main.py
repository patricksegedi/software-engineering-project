from voice_recorder import VoiceRecorder
from audio_to_text import AudioToText
from wake_word_activation import WakeWordActivation
from speaker_verification import SpeakerVerifier
from command_processor import CommandProcessor
from playsound import playsound
import pyttsx3

def handle_commands(user_name):
    """사용자 인증 후 명령어를 처리하는 함수"""
    command_processor = CommandProcessor()
    audio_to_text = AudioToText()
    recorder = VoiceRecorder()
    
    # 시스템 종료 플래그
    should_terminate = False
    
    print("📝 명령어 대기 모드 시작... / Starting command mode...")
    
    while True:
        try:
            print("🎙️ 명령어를 말씀해주세요... / Please say a command...")
            recorder.record()
            
            # 음성을 텍스트로 변환
            transcript = audio_to_text.transcribe("voice_sample.wav")
            
            if transcript:
                print(f"인식된 음성 / Recognized: {transcript}")
                
                # "Hello"가 포함되어 있으면 wake word 모드로 돌아가기
                if "hello" in transcript.lower():
                    print("Wake word가 감지되어 메인 모드로 돌아갑니다. / Wake word detected, returning to main mode.")
                    print("=" * 50)
                    break
                
                # 명령어 처리
                command_found, response = command_processor.process_command(transcript)
                
                if command_found:
                    command_processor.speak_response(response)
                    
                    # terminate 명령어 처리
                    if "terminate" in transcript.lower():
                        print("\n시스템을 종료합니다... / Shutting down system...")
                        should_terminate = True
                        break
                else:
                    # 인식되지 않은 명령어도 음성으로 안내
                    error_message = "I didn't understand that command. Please try again."
                    print(f"❌ {error_message}")
                    command_processor.speak_response(error_message)
                
                print("\n다음 명령어를 기다리는 중... / Waiting for next command...")
                print("-" * 30)
            else:
                print("음성을 인식하지 못했습니다. 다시 시도해주세요. / Could not recognize voice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n명령어 모드를 종료합니다. / Exiting command mode.")
            break
        except Exception as e:
            print(f"명령어 처리 중 오류 / Error during command processing: {e}")
            continue
    
    # should_terminate 플래그 반환
    return should_terminate

def main():
    print("=== 스마트 스피커 시작 / Smart Speaker Started ===")
    print("'Hello'라고 말하면 음성 인식이 시작됩니다. / Say 'Hello' to start voice recognition.")
    print("프로그램을 종료하려면 Ctrl+C를 누르세요. / Press Ctrl+C to exit.")
    print()
    
    while True:
        try:
            VoiceRecorder().record()

            wake = WakeWordActivation(AudioToText(), "Hello")

            wake_detected = wake.is_activated("voice_sample.wav")
            print(f"Wake word 감지 / Detected: {wake_detected}")
            
            if wake_detected:
                verifier = SpeakerVerifier()
                identified_user, score = verifier.identify_speaker("voice_sample.wav")
                
                if identified_user:
                    message = f"Hello, {identified_user}! How can I assist you?"
                    print(message)
                    
                    # TTS로 개인화된 음성 응답
                    try:
                        tts = pyttsx3.init()
                        tts.setProperty('rate', 150)
                        tts.setProperty('volume', 0.9)
                        
                        print(f"🔊 음성으로 말하는 중 / Speaking: {message}")
                        tts.say(message)
                        tts.runAndWait()
                        print("✅ 음성 출력 완료 / Voice output completed")
                    except Exception as e:
                        print(f"TTS 오류: {e}")
                        print("음성 출력에 실패했지만 계속 진행합니다.")
                    
                    # 명령어 처리 모드 진입
                    print(f"\n🎯 {identified_user}님, 명령어를 말씀해주세요! / {identified_user}, please say a command!")
                    print("사용 가능한 명령어 / Available commands:")
                    print("- Turn on the light")
                    print("- What is your name") 
                    print("- What is the temperature")
                    print("- Terminate (프로그램 종료 / Exit program)")
                    print()
                    
                    should_terminate = handle_commands(identified_user)
                    
                    if should_terminate:
                        print("\n프로그램을 완전히 종료합니다. / Terminating program.")
                        import sys
                        sys.exit(0)
                    else:
                        # 명령어 처리 완료 후 다시 wake word 대기로 돌아감
                        print("\n=== Wake Word 대기 모드로 돌아갑니다 / Returning to Wake Word Mode ===")
                        print()
                else:
                    print("음성 인식에 실패했습니다. 등록되지 않은 사용자입니다. / Voice recognition failed. Unregistered user.")
                    playsound("voices/invalid.mp3")
                    print()
            # else 부분 제거 - Wake word 감지 실패 시 조용히 다시 대기
            
        except KeyboardInterrupt:
            print("\n\n스마트 스피커를 종료합니다. / Shutting down smart speaker.")
            break
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            continue

'''        
        else:
            print("No activation!")
            playsound("voices/invalid.mp3")
'''

if __name__ == "__main__":
    main()