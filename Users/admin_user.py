from user import User

class AdminUser(User):
    def __init__(self, user_id, name, voice=None):
        super().__init__(user_id, name, voice)
        self.role = "admin"