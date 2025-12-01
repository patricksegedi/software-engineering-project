from smarterspeaker.speaker.audio_to_text import AudioToText

class WakeWordActivation:
    def __init__(self, audio_to_text, keyword):
        self.audio_to_text = audio_to_text
        self.keyword = keyword.lower()

    def is_activated(self, audio_file):
        text = self.audio_to_text.transcribe(audio_file)
        print(f"[DEBUG] Transcribed text: '{text}'")
        print(f"[DEBUG] Looking for keyword: '{self.keyword}'")
        result = self.keyword in text
        print(f"[DEBUG] Wake word found: {result}")
        return result