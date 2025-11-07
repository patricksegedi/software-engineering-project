#!/usr/bin/env python3
"""
명령어 처리 모듈
사용자의 음성 명령을 인식하고 적절한 응답을 생성합니다.
"""

import pyttsx3

class CommandProcessor:
    def __init__(self):
        """명령어 처리기 초기화"""
        self.commands = {
            "turn on the light": "OK, I will turn on the light.",
            "what is your name": "Hi, my name is Bob.",
            "what is the temperature": "It's 13 degrees.",
            "terminate": "Goodbye! System shutting down."
        }
        
    def process_command(self, transcript_text):
        """
        음성 변환 텍스트에서 명령어를 찾고 처리합니다.
        
        Args:
            transcript_text (str): 음성에서 변환된 텍스트
            
        Returns:
            tuple: (명령어_발견됨, 응답_메시지)
        """
        # 텍스트를 소문자로 변환하고 공백 정리
        clean_text = transcript_text.lower().strip()
        
        print(f"🔍 명령어 분석 중 / Analyzing command: '{clean_text}'")
        
        # 등록된 명령어들과 비교
        for command, response in self.commands.items():
            if command in clean_text:
                print(f"✅ 명령어 매칭 / Command matched: '{command}'")
                return True, response
        
        print("❌ 인식된 명령어가 없습니다. / No recognized command.")
        return False, "I didn't understand that command. Please try again."
    
    def speak_response(self, message):
        """
        TTS로 응답을 음성으로 출력합니다.
        
        Args:
            message (str): 말할 메시지
        """
        print(f"🔊 음성 응답 / Voice response: {message}")
        
        import platform
        import subprocess
        
        os_name = platform.system()
        
        # OS별 TTS 처리
        if os_name == "Darwin":  # macOS
            try:
                subprocess.run(['say', message], check=True)
                print("✅ macOS 음성 출력 완료 / macOS voice output completed")
                return
            except:
                pass
                
        elif os_name == "Windows":  # Windows
            try:
                # Windows PowerShell의 TTS 사용
                command = f'PowerShell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{message}\')"'
                subprocess.run(command, shell=True, check=True)
                print("✅ Windows 음성 출력 완료 / Windows voice output completed")
                return
            except:
                pass
                
        elif os_name == "Linux":  # Linux
            try:
                # espeak 사용 (설치 필요: sudo apt-get install espeak)
                subprocess.run(['espeak', message], check=True)
                print("✅ Linux 음성 출력 완료 / Linux voice output completed")
                return
            except:
                pass
        
        # 모든 OS에서 실패시 pyttsx3 사용
        try:
            tts = pyttsx3.init()
            tts.setProperty('rate', 150)
            tts.setProperty('volume', 0.9)
            tts.say(message)
            tts.runAndWait()
            print("✅ pyttsx3로 음성 출력 완료 / pyttsx3 voice output completed")
        except Exception as e:
            print(f"TTS 완전 실패 / TTS completely failed: {e}")
            print("음성 출력을 사용할 수 없습니다. / Voice output is not available.")
    
    def get_available_commands(self):
        """사용 가능한 명령어 목록을 반환합니다."""
        return list(self.commands.keys())
    
    def add_command(self, command, response):
        """새로운 명령어를 추가합니다."""
        self.commands[command.lower()] = response
        print(f"새 명령어 추가됨 / New command added: '{command}' -> '{response}'")