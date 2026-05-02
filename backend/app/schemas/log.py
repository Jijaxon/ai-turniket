"""
Pydantic schemas for AccessLog and Auth endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Access Log ────────────────────────────────────────────────────────────────

class AccessLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: Optional[str]
    timestamp: datetime
    status: str
    confidence: Optional[float]
    reason: Optional[str]
    ip_address: Optional[str]

    class Config:
        from_attributes = True


class LogList(BaseModel):
    total: int
    logs: list[AccessLogResponse]


class DailyStats(BaseModel):
    date: str
    total: int
    allowed: int
    denied: int
    unique_users: int


class StatsResponse(BaseModel):
    today: DailyStats
    total_users: int
    total_logs: int
    recent_logs: list[AccessLogResponse]


# ── Face Recognition ──────────────────────────────────────────────────────────

class RecognizeRequest(BaseModel):
    image: str = Field(..., description="Base64-encoded image from webcam")
    device_id: Optional[str] = Field(None, max_length=100)


class RecognizeResponse(BaseModel):
    status: str          # "allowed" | "denied"
    user_id: Optional[int] = None
    name: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
