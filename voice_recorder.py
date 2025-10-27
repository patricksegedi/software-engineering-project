import sounddevice as sd
import wavio

class VoiceRecorder:

    def record(self, filename="voice_sample.wav", duration=3):
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
'''    
if __name__ == "__main__":
    VoiceRecorder().record()
'''