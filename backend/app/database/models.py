"""
SQLAlchemy ORM models for the Turniket system.
"""

import json
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Enum, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    """Registered user whose face is enrolled in the system."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    # Face encoding stored as JSON array of 128 floats
    face_encoding = Column(Text, nullable=True)
    face_image_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    access_logs = relationship("AccessLog", back_populates="user", lazy="dynamic")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def get_face_encoding(self) -> list[float] | None:
        """Deserialise face encoding from JSON string."""
        if self.face_encoding:
            return json.loads(self.face_encoding)
        return None

    def set_face_encoding(self, encoding: list[float]) -> None:
        """Serialise face encoding to JSON string."""
        self.face_encoding = json.dumps(encoding)

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r}>"


class AccessLog(Base):
    """Record of every recognition attempt – allowed or denied."""

    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(
        Enum("allowed", "denied", name="access_status"),
        nullable=False,
        index=True,
    )
    confidence = Column(Float, nullable=True)           # recognition confidence 0-1
    reason = Column(String(200), nullable=True)         # denial reason if applicable
    ip_address = Column(String(50), nullable=True)
    device_id = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="access_logs")

    def __repr__(self) -> str:
        return f"<AccessLog id={self.id} status={self.status} user_id={self.user_id}>"


class AdminUser(Base):
    """Admin accounts that can manage the system via JWT-protected routes."""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AdminUser id={self.id} username={self.username!r}>"
