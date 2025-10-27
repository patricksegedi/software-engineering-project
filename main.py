from voice_recorder import VoiceRecorder
from audio_to_text import AudioToText
from wake_word_activation import WakeWordActivation
from speaker_verification import SpeakerVerifier
from playsound import playsound

def main():
    while True:
        VoiceRecorder().record()

        wake = WakeWordActivation(AudioToText(), "Hello")

        if wake.is_activated("voice_sample.wav") and SpeakerVerifier().verify("voice_sample.wav", "voice_samples/patrick"):
            print("Hello, how can I assist you?")
            playsound("voices/valid.mp3")
            continue

'''        
        else:
            print("No activation!")
            playsound("voices/invalid.mp3")
'''

if __name__ == "__main__":
    main()