"""
Pydantic schemas for User endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    email: EmailStr
    department: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Payload for POST /users/add – includes base64 face image."""
    face_image: str = Field(..., description="Base64-encoded JPEG/PNG of the user's face")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    has_face_encoding: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, user) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            department=user.department,
            is_active=user.is_active,
            has_face_encoding=user.face_encoding is not None,
            created_at=user.created_at,
        )


class UserList(BaseModel):
    total: int
    users: list[UserResponse]
