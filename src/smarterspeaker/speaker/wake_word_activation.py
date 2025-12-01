from smarterspeaker.speaker.audio_to_text import AudioToText

class WakeWordActivation:
    def __init__(self, audio_to_text, keyword):
        self.audio_to_text = audio_to_text
        self.keyword = keyword.lower()

    def is_activated(self, audio_file):
        text = self.audio_to_text.transcribe(audio_file)
        return self.keyword in text