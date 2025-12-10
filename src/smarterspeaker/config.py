from pathlib import Path
import os
from dotenv import load_dotenv

# Wake words
WAKE_WORDS = ["Activate, Hello, Hi, Help me"]

# Speaker verification
DIRECTORY_PATH = Path("voice_samples")
THRESHOLD = 0.16

# Audio recording
SAMPLE_RATE = 16000
RECORD_SECONDS = 3
VOICE_INPUT = "voice_sample.wav"

load_dotenv()

MASTER_KEY = os.getenv("MASTER_KEY", "01046480328")  # 원하는 값으로