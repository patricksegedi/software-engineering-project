class RestrictionDbo:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"RestrictionListDbo(id={self.id}, name='{self.name}'"
