from pathlib import Path
from .speaker.voice_recorder import VoiceRecorder
from .speaker.audio_to_text import AudioToText
from .speaker.wake_word_activation import WakeWordActivation
from .speaker.speaker_verification import SpeakerVerifier
from .speaker.speaker_active import speaker_activate
from playsound import playsound
from .config import THRESHOLD
import json

# Base directory of smarterspeaker/
BASE_DIR = Path(__file__).resolve().parent

# users.JSON lives inside smarterspeaker/
USERS_FILE = BASE_DIR / "users.JSON"

# voice_samples also lives inside smarterspeaker/
VOICE_SAMPLES_DIR = BASE_DIR / "voice_samples"

def main():

    with open(USERS_FILE, "r") as file:
        users = json.load(file)  # assuming it's valid JSON

    # Create single instances to avoid re-initialization
    voice_recorder = VoiceRecorder()
    audio_processor = AudioToText()
    
    while True:
        recorded_file = voice_recorder.record()
        wake = WakeWordActivation(audio_processor, "Hello")

        if wake.is_activated("voice_sample.wav"):
            user = SpeakerVerifier().identify_speaker(recorded_file, users, THRESHOLD)
            if user is not None:
                # Skip the first greeting - AI will handle it
                speaker_activate(user, audio_processor, voice_recorder)
                break
            else:
                invalid_path = BASE_DIR / "voices" / "invalid.mp3"
                print("No activation!")
                playsound(str(invalid_path))