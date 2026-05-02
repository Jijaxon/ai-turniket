"""
Auth service: admin login and token management.
"""

from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import verify_password, create_access_token, hash_password
from ..database.models import AdminUser
from ..config import get_settings

settings = get_settings()


def authenticate_admin(db: Session, username: str, password: str) -> AdminUser:
    """
    Verify admin credentials.
    Raises HTTPException 401 if invalid.
    """
    admin = db.query(AdminUser).filter(
        AdminUser.username == username,
        AdminUser.is_active == True,
    ).first()

    if not admin or not verify_password(password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin


def create_token_for_admin(admin: AdminUser) -> dict:
    """Return a token response dict for the given admin."""
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": admin.username, "admin_id": admin.id},
        expires_delta=expires,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": int(expires.total_seconds()),
    }


def seed_admin_if_needed(db: Session) -> None:
    """Create the default admin account on first startup."""
    exists = db.query(AdminUser).filter(
        AdminUser.username == settings.ADMIN_USERNAME
    ).first()
    if not exists:
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
        )
        db.add(admin)
        db.commit()
