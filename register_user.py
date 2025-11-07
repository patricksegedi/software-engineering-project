#!/usr/bin/env python3
"""
사용자 음성 등록 도구
새로운 사용자의 음성을 등록하여 화자 인식 시스템에 추가합니다.
"""

import os
import time
from voice_recorder import VoiceRecorder

def register_new_user():
    """새로운 사용자를 등록하는 함수"""
    
    print("=== 사용자 음성 등록 시스템 ===")
    print()
    
    # 사용자 이름 입력
    while True:
        name = input("등록할 이름을 입력하세요: ").strip()
        if name:
            break
        print("이름을 입력해주세요.")
    
    # 사용자 폴더 생성
    user_folder = f"voice_samples/{name}"
    os.makedirs(user_folder, exist_ok=True)
    
    print(f"\n'{name}' 사용자를 등록합니다.")
    print("다음 5개의 문장을 차례대로 읽어주세요.")
    print("각 문장 후 2초간 기다린 후 다음 문장으로 넘어갑니다.")
    print()
    
    # 녹음할 문장들
    sentences = [
        "Hello",
        "What is your name?",
        "How is the weather?",
        "What is the temperature?",
        "Turn on the TV"
    ]
    
    recorder = VoiceRecorder()
    
    for i, sentence in enumerate(sentences, 1):
        print(f"[{i}/5] 다음 문장을 읽어주세요:")
        print(f"'{sentence}'")
        print()
        
        input("준비되면 Enter를 누르세요...")
        
        # 음성 녹음
        print("🎙️ 녹음 중... 문장을 읽어주세요!")
        recorder.record()
        
        # 파일을 사용자 폴더로 이동
        sample_file = f"{user_folder}/sample{i}.wav"
        os.rename("voice_sample.wav", sample_file)
        
        print(f"✅ 샘플 {i} 저장 완료: {sample_file}")
        print()
        
        if i < len(sentences):
            print("2초 후 다음 문장으로 넘어갑니다...")
            time.sleep(2)
            print()
    
    print(f"🎉 '{name}' 사용자 등록이 완료되었습니다!")
    print(f"총 {len(sentences)}개의 음성 샘플이 '{user_folder}' 폴더에 저장되었습니다.")
    print()
    print("이제 main.py를 실행하여 음성 인식을 테스트해보세요.")

if __name__ == "__main__":
    try:
        register_new_user()
    except KeyboardInterrupt:
        print("\n\n등록이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")