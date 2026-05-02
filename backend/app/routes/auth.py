"""
Auth routes: POST /auth/login
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.log import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_admin, create_token_for_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Admin login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an admin user and return a JWT access token.

    Example request:
    ```json
    { "username": "admin", "password": "admin123" }
    ```
    """
    admin = authenticate_admin(db, payload.username, payload.password)
    return create_token_for_admin(admin)
