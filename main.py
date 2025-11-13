from voice_recorder import VoiceRecorder
from audio_to_text import AudioToText
from wake_word_activation import WakeWordActivation
from speaker_verification import SpeakerVerifier
from playsound import playsound
from config import THRESHOLD

import json

def main():

    with open("users.json", "r") as file:
        users = json.load(file)

    while True:
        recorded_file = VoiceRecorder().record()
        wake = WakeWordActivation(AudioToText(), "Hello")

        if wake.is_activated("voice_sample.wav"):
            user = SpeakerVerifier().identify_speaker(recorded_file, users, THRESHOLD)
            if user is not None:
                path = f"voice_samples/{user}/voices/valid.wav"
                print(f"Hi, {user}, how can I assist you?")
                playsound(path)
                continue
            else:
                print("No activation!")
                playsound("voices/invalid.mp3")

if __name__ == "__main__":
    main()