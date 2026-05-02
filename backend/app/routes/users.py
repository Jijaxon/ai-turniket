"""
User management routes.
All routes are protected by JWT admin authentication.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.database.db import get_db
from app.database.models import User
from app.schemas.user import UserCreate, UserResponse, UserList, UserUpdate
from app.services.face_recognition_service import face_service
from app.utils.image_processing import decode_base64_image

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/add",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user with face enrollment",
)
def add_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """
    Register a new user and enrol their face.

    - Decodes the base64 face image
    - Extracts the 128-d face encoding
    - Stores user + encoding in the database
    - Reloads in-memory cache
    """
    # Check duplicate email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{payload.email}' already exists.",
        )

    # Decode image and extract face encoding
    try:
        bgr_image = decode_base64_image(payload.face_image)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    encoding = face_service.extract_encoding(bgr_image)
    if encoding is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No face detected in the provided image. Please use a clear frontal photo.",
        )

    # Persist user
    user = User(name=payload.name, email=payload.email, department=payload.department)
    user.set_face_encoding(encoding.tolist())
    db.add(user)
    db.commit()
    db.refresh(user)

    # Reload in-memory cache so new user is immediately recognised
    face_service.reload_encodings(db)
    logger.info("New user registered: id=%d name=%s", user.id, user.name)

    return UserResponse.from_orm_model(user)


@router.get("/", response_model=UserList, summary="List all registered users")
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return UserList(
        total=total,
        users=[UserResponse.from_orm_model(u) for u in users],
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm_model(user)


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user details")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    face_service.reload_encodings(db)
    return UserResponse.from_orm_model(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    face_service.reload_encodings(db)
    return None
