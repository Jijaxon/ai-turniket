"""
Application configuration using pydantic-settings.
All settings can be overridden via environment variables or a .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "AI Turniket System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────────────────────
    # Switch to PostgreSQL DSN in production:
    # DATABASE_URL: str = "postgresql://user:pass@localhost:5432/turniket"
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/turniket_db"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "super-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Admin credentials (seeded on first run) ───────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # ── Face recognition ──────────────────────────────────────────────────────
    FACE_DISTANCE_THRESHOLD: float = 0.55   # lower = stricter
    MAX_IMAGE_SIZE_MB: int = 5

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton – import this everywhere."""
    return Settings()
