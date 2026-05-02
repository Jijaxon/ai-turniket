"""
Face recognition route: POST /recognize-face
This endpoint is intentionally unauthenticated so it can be
called directly by the turniket hardware/kiosk.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import AccessLog
from app.schemas.log import RecognizeRequest, RecognizeResponse
from app.services.face_recognition_service import face_service
from app.utils.image_processing import decode_base64_image

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Recognition"])


@router.post(
    "/recognize-face",
    response_model=RecognizeResponse,
    summary="Perform real-time face recognition",
)
async def recognize_face(
    payload: RecognizeRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Receive a base64 webcam snapshot, run face recognition,
    log the result, and return an access decision.

    **Example allowed response:**
    ```json
    {
      "status": "allowed",
      "user_id": 1,
      "name": "John Doe",
      "confidence": 0.92,
      "reason": null,
      "timestamp": "2024-01-15T10:30:00"
    }
    ```

    **Example denied response:**
    ```json
    {
      "status": "denied",
      "user_id": null,
      "name": null,
      "confidence": 0.31,
      "reason": "Unknown person – face not recognised",
      "timestamp": "2024-01-15T10:30:01"
    }
    ```
    """
    # Decode image
    try:
        bgr_image = decode_base64_image(payload.image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Run recognition
    result = face_service.recognize(bgr_image)

    # Persist access log
    log = AccessLog(
        user_id=result.get("user_id"),
        status=result["status"],
        confidence=result.get("confidence"),
        reason=result.get("reason"),
        ip_address=request.client.host if request.client else None,
        device_id=payload.device_id,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.commit()

    logger.info(
        "Access %s | user_id=%s | confidence=%s | ip=%s",
        result["status"], result.get("user_id"), result.get("confidence"),
        log.ip_address,
    )

    return RecognizeResponse(**result)


@router.get(
    "/cache/status",
    summary="Check in-memory face encoding cache size",
    tags=["Recognition"],
)
def cache_status():
    """Returns number of face encodings currently cached."""
    return {"cached_encodings": face_service.get_cache_size()}


@router.post(
    "/cache/reload",
    summary="Force reload face encodings from database",
    tags=["Recognition"],
)
def reload_cache(db: Session = Depends(get_db)):
    """Manually trigger a cache reload (useful after bulk imports)."""
    count = face_service.reload_encodings(db)
    return {"message": f"Cache reloaded with {count} encodings"}
