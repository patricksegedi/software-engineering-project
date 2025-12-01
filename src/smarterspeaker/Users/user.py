class User:
    def __init__(self, user_id, name=None, voice=None, role="user"):
        self.user_id = user_id
        self.name = name
        self.voice = voice
        self.role = role

    def get_name(self):
        return self.name

    def set_voice(self, voice):
        self.voice = voice