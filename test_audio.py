#!/usr/bin/env python3
"""
AudioToText 테스트 스크립트
"""

from audio_to_text import AudioToText
import time

def test_transcribe():
    print("🧪 AudioToText 테스트 시작")
    
    try:
        # AudioToText 객체 생성
        print("1️⃣ AudioToText 객체 생성 중...")
        audio_processor = AudioToText()
        print("✅ 객체 생성 완료")
        
        # 파일 변환 테스트
        print("2️⃣ command.wav 파일 변환 시작...")
        start_time = time.time()
        
        result = audio_processor.transcribe("command.wav")
        
        end_time = time.time()
        print(f"✅ 변환 완료! 소요시간: {end_time - start_time:.2f}초")
        print(f"🎯 결과: '{result}'")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcribe()