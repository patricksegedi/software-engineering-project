# src/smarterspeaker/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    LargeBinary,
    Float,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .db import Base


class SpeakerProfile(Base):
    __tablename__ = "speaker_profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    meta_json = Column(Text, nullable=False)


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    order_index = Column(Integer, default=0)

    devices = relationship("Device", back_populates="zone")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # light/tv/ac/door
    status = Column(String(50), default="off")
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)

    zone = relationship("Zone", back_populates="devices")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # ✅ 이름 컬럼 추가 (DB에 ALTER TABLE로 만들어둔 name과 매칭)
    name = Column(String(100), nullable=True)

    hashed_password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    family_role = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # 1:1 관계 – 음성 프로필
    voice_profile = relationship(
        "UserVoiceProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserVoiceProfile(Base):
    __tablename__ = "user_voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # DB에는 audio_path, embedding_json 대신 voice_blob 하나만 사용
    voice_blob = Column(LargeBinary, nullable=False)

    user = relationship("User", back_populates="voice_profile")
