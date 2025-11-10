class UserDbo:
    def __init__(self, id=None, name=None, role=None, restrictions_link=None):
        self.id = id
        self.name = name
        self.role = role
        self.restrictions_link = restrictions_link

    def __repr__(self):
        return f"UserDbo(id={self.id}, name='{self.name}', role='{self.role}', restrictions_link={self.restrictions_link})"
