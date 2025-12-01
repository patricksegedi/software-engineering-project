import torch
from TTS.api import TTS

from torch.serialization import add_safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

print(device)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

tts.tts_to_file(
    text="Hello Nick, how can I help you?",
    #text="태희님, 도와드릴게요.",
    #file_path="aaron.wav", speaker="Aaron Dreschner",
    file_path="alexandra.wav", speaker="Alexandra Hisakawa",
    #file_path="andrew.wav", speaker="Andrew Chipper",
    #file_path="asya.wav", speaker="Asya Anara",
    #language="ko"
    language="en"
)