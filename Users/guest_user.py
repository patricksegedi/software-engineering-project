from user import User

class GuestUser(User):
    def __init__(self, voice=None):
        super().__init__(user_id="guest", name="Guest", voice=voice, role="guest")