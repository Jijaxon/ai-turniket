# """
# Security helpers: JWT creation/verification and password hashing.
# """
#
# from datetime import datetime, timedelta
# from typing import Optional
#
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
#
# from ..config import get_settings
#
# settings = get_settings()
#
# # ── Password hashing ──────────────────────────────────────────────────────────
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#
#
# def hash_password(plain: str) -> str:
#     return pwd_context.hash(plain)
#
#
# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)
#
#
# # ── JWT ───────────────────────────────────────────────────────────────────────
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """Create a signed JWT token."""
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (
#         expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#
#
# def decode_token(token: str) -> dict:
#     """Decode and validate a JWT token. Raises HTTPException on failure."""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         return payload
#     except JWTError:
#         raise credentials_exception
#
#
# # ── FastAPI dependency ────────────────────────────────────────────────────────
#
# def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
#     """Dependency: require a valid admin JWT."""
#     return decode_token(token)

"""
Security helpers: JWT creation/verification and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..config import get_settings

settings = get_settings()

# ── Password hashing ──────────────────────────────────────────────────────────
# bcrypt 72 bayt cheklovini hisobga olish
def _prepare_password(plain: str) -> str:
    """Ensure password is within bcrypt's 72-byte limit."""
    if isinstance(plain, str):
        plain_bytes = plain.encode('utf-8')
        if len(plain_bytes) > 72:
            return plain_bytes[:72].decode('utf-8', errors='ignore')
    return plain

# CryptContext ni ishga tushirishdan oldin bir oz sozlash
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Optimal rounds
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain: str) -> str:
    """Hash a password with bcrypt, handling 72-byte limit."""
    return pwd_context.hash(_prepare_password(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(_prepare_password(plain), hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises HTTPException on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency: require a valid admin JWT."""
    return decode_token(token)