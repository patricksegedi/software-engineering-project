# model.py (example)
from dataclasses import dataclass

@dataclass
class UserDbo:
    name: str
    role: str
    email: str
    phone_number: str
    password: str
    restriction_list: int | None = None   # 👈 match DB column name & INT type
