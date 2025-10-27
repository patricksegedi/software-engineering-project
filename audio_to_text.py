from faster_whisper import WhisperModel
import string

class AudioToText:

    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def clean_text(self, text):
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator).lower()

    def transcribe(self, filename):
        segments, info = self.model.transcribe(filename)

        print(f"Detected language: {info.language} ({info.language_probability:.2f})")
        print("Transcript:")

        transcript = ""
        for segment in segments:
            print(f"[{segment.start:.2f}-{segment.end:.2f}] {segment.text}")
            transcript += segment.text + " "
        return self.clean_text(transcript.strip())