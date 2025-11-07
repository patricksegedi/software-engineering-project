import sounddevice as sd
import wavio
import numpy as np
import webrtcvad
import time

class VoiceRecorder:

    def __init__(self, sample_rate=16000, vad_aggressiveness=2):
        """
        초기화
        vad_aggressiveness: 0-3 (0이 가장 민감, 3이 가장 둔감)
        """
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        
    def record(self, filename="voice_sample.wav", duration=3):
        """기존 단순 녹음 방식 (고정 시간)"""
        samplerate = 16000
        print("🎙️ Speak now…")
        audio = sd.rec(int(duration * samplerate),
                       samplerate=samplerate,
                       channels=1,
                       dtype='int16')
        sd.wait()
        wavio.write(filename, audio, samplerate, sampwidth=2)
        print(f"✅ Saved {filename}")
        return filename
    
    def record_with_vad(self, filename="voice_sample.wav", min_duration=1.0, max_duration=10.0, 
                        silence_duration=1.5, pre_recording_buffer=0.5):
        """
        VAD를 사용한 스마트 녹음
        min_duration: 최소 녹음 시간 (초)
        max_duration: 최대 녹음 시간 (초)
        silence_duration: 침묵으로 간주할 시간 (초)
        pre_recording_buffer: 음성 시작 전 버퍼 시간 (초)
        """
        print("🎙️ 말씀해주세요... (음성을 감지하면 녹음을 시작합니다) / Please speak... (Recording starts when voice is detected)")
        
        frame_duration = 30  # 밀리초
        frame_size = int(self.sample_rate * frame_duration / 1000)
        
        # 전체 오디오 저장용
        audio_frames = []
        
        # 음성 감지 변수
        speech_detected = False
        speech_started = False
        silence_start_time = None
        recording_start_time = time.time()
        
        # 사전 녹음 버퍼
        pre_buffer_frames = []
        pre_buffer_size = int(pre_recording_buffer * 1000 / frame_duration)
        
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16',
                          blocksize=frame_size) as stream:
            
            while True:
                current_time = time.time()
                elapsed_time = current_time - recording_start_time
                
                # 최대 녹음 시간 체크
                if elapsed_time > max_duration:
                    print("⏱️ 최대 녹음 시간에 도달했습니다. / Maximum recording time reached.")
                    break
                
                # 오디오 프레임 읽기
                audio_chunk, _ = stream.read(frame_size)
                audio_chunk = audio_chunk.flatten()
                
                # VAD로 음성 감지
                is_speech = self.vad.is_speech(audio_chunk.tobytes(), self.sample_rate)
                
                # 사전 버퍼 관리
                if not speech_started:
                    pre_buffer_frames.append(audio_chunk)
                    if len(pre_buffer_frames) > pre_buffer_size:
                        pre_buffer_frames.pop(0)
                
                if is_speech:
                    if not speech_started:
                        speech_started = True
                        print("🔴 녹음 시작! / Recording started!")
                        # 사전 버퍼의 프레임들을 먼저 추가
                        audio_frames.extend(pre_buffer_frames)
                    
                    speech_detected = True
                    silence_start_time = None
                    audio_frames.append(audio_chunk)
                    
                else:
                    if speech_started:
                        audio_frames.append(audio_chunk)
                        
                        if silence_start_time is None:
                            silence_start_time = current_time
                        elif current_time - silence_start_time > silence_duration:
                            # 충분한 침묵이 감지되면 녹음 종료
                            if len(audio_frames) * frame_duration / 1000 >= min_duration:
                                print("🔇 음성 종료 감지 / End of speech detected")
                                break
                
                # 음성이 시작되었고 최소 시간이 지났는지 체크
                if speech_started and elapsed_time > min_duration + pre_recording_buffer:
                    # 상태 표시 (선택사항)
                    pass
        
        if not speech_detected:
            print("⚠️ 음성이 감지되지 않았습니다. 다시 시도해주세요. / No voice detected. Please try again.")
            return None
        
        # 오디오 저장
        if audio_frames:
            audio_data = np.concatenate(audio_frames)
            wavio.write(filename, audio_data, self.sample_rate, sampwidth=2)
            print(f"✅ 저장 완료 / Saved: {filename}")
            return filename
        else:
            print("⚠️ 녹음된 오디오가 없습니다. / No audio recorded.")
            return None

# 기본 record 메서드를 VAD 버전으로 교체
VoiceRecorder.record_original = VoiceRecorder.record
VoiceRecorder.record = lambda self, filename="voice_sample.wav": self.record_with_vad(filename)

'''    
if __name__ == "__main__":
    VoiceRecorder().record()
'''