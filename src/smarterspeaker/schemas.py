from pydantic import BaseModel, EmailStr
from typing import Optional

# ----- Users -----

class UserBase(BaseModel):
    email: EmailStr
    age: Optional[int] = None
    family_role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

# ----- Voice Profiles -----

class VoiceProfileBase(BaseModel):
    label: Optional[str] = None

class VoiceProfileCreate(VoiceProfileBase):
    file_path: str

class VoiceProfileOut(VoiceProfileBase):
    id: int
    user_id: int
    file_path: str
    is_active: bool

    class Config:
        orm_mode = True


# ----- Zone -----

class ZoneBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    order_index: int = 0

class ZoneCreate(ZoneBase):
    pass

class ZoneOut(ZoneBase):
    id: int

    class Config:
        orm_mode = True


# ----- Devices -----

class DeviceBase(BaseModel):
    name: str
    type: str
    status: str
    zone_id: int

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    status: Optional[str] = None

class DeviceOut(DeviceBase):
    id: int
    zone: ZoneOut

    class Config:
        orm_mode = True
