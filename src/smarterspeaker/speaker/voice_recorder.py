import sounddevice as sd
import wavio
from smarterspeaker.config import SAMPLE_RATE, RECORD_SECONDS, VOICE_INPUT

class VoiceRecorder:

    def record(self, filename=VOICE_INPUT, duration=RECORD_SECONDS):
        samplerate = SAMPLE_RATE
        print("🎙️ Speak now…")
        audio = sd.rec(int(duration * samplerate),
                       samplerate=samplerate,
                       channels=1,
                       dtype='int16')
        sd.wait()
        wavio.write(filename, audio, samplerate, sampwidth=2)
        print(f"✅ Saved {filename}")
        return filename
    
if __name__ == "__main__":
    VoiceRecorder().record()