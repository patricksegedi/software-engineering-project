from pathlib import Path

# Wake words
WAKE_WORDS = ["Activate, Hello, Hi, Help me"]

# Speaker verification
DIRECTORY_PATH = Path("voice_samples")
THRESHOLD = 0.3

# Audio recording
SAMPLE_RATE = 16000
RECORD_SECONDS = 5
VOICE_INPUT = "voice_sample.wav"