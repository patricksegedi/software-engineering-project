# src/smarterspeaker/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ===========================
# User Schemas
# ===========================

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None          # ✅ 이름 필드 추가
    age: Optional[int] = None
    family_role: Optional[str] = None


class UserCreate(UserBase):
    password: str                       # 비밀번호
    master_key: Optional[str] = None    # ✅ 회원가입 시에만 받는 마스터키


class UserOut(UserBase):
    id: int
    is_admin: bool

    # SQLAlchemy 모델에서 바로 변환 가능하게
    model_config = {"from_attributes": True}


# ===========================
# Zone Schemas
# ===========================

class ZoneBase(BaseModel):
    name: str
    display_name: str
    order_index: int


class ZoneCreate(ZoneBase):
    pass


class ZoneOut(ZoneBase):
    id: int

    model_config = {"from_attributes": True}


# ===========================
# Device Schemas
# ===========================

class DeviceBase(BaseModel):
    name: str
    type: str
    zone_id: int
    status: str = "off"


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    status: Optional[str] = None


class DeviceOut(DeviceBase):
    id: int

    model_config = {"from_attributes": True}
