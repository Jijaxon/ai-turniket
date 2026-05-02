"""
Face Recognition Service
========================
Manages known face encodings (loaded from DB), performs real-time
comparison, and caches results for performance.
"""

import logging
import time
from threading import Lock
from typing import Optional

import face_recognition
import numpy as np
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import User
from app.utils.image_processing import bgr_to_rgb, resize_for_recognition

settings = get_settings()
logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """
    Singleton-like service that maintains an in-memory cache of face encodings.
    Call `reload_encodings(db)` when users are added or updated.
    """

    def __init__(self):
        self._lock = Lock()
        # user_id → (name, encoding_vector)
        self._known: dict[int, tuple[str, np.ndarray]] = {}
        self._last_reload: float = 0.0

    # ── Cache management ──────────────────────────────────────────────────────

    def reload_encodings(self, db: Session) -> int:
        """
        Load all active users with face encodings from the database into memory.
        Returns number of encodings loaded.
        Thread-safe.
        """
        users = (
            db.query(User)
            .filter(User.is_active == True, User.face_encoding.isnot(None))
            .all()
        )

        new_cache: dict[int, tuple[str, np.ndarray]] = {}
        for user in users:
            encoding_list = user.get_face_encoding()
            if encoding_list:
                new_cache[user.id] = (user.name, np.array(encoding_list, dtype=np.float64))

        with self._lock:
            self._known = new_cache
            self._last_reload = time.time()

        logger.info("Face encodings reloaded: %d entries", len(new_cache))
        return len(new_cache)

    def get_cache_size(self) -> int:
        return len(self._known)

    # ── Encoding extraction ───────────────────────────────────────────────────

    def extract_encoding(self, bgr_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract a 128-d face encoding from a BGR OpenCV image.
        Returns None if no face is detected.
        Only the first detected face is used.
        """
        # Resize for speed, then convert to RGB for face_recognition
        small = resize_for_recognition(bgr_image, max_width=640)
        rgb = bgr_to_rgb(small)

        locations = face_recognition.face_locations(rgb, model="hog")
        if not locations:
            return None

        encodings = face_recognition.face_encodings(rgb, known_face_locations=locations)
        if not encodings:
            return None

        return encodings[0]

    # ── Recognition ──────────────────────────────────────────────────────────

    def recognize(
        self, bgr_image: np.ndarray
    ) -> dict:
        """
        Main recognition pipeline:
        1. Extract encoding from incoming image
        2. Compare against cached known encodings
        3. Return structured result dict

        Returns:
            {
                "status": "allowed"|"denied",
                "user_id": int|None,
                "name": str|None,
                "confidence": float|None,
                "reason": str|None,
            }
        """
        start = time.perf_counter()

        # Step 1 – extract encoding
        incoming = self.extract_encoding(bgr_image)
        if incoming is None:
            elapsed = time.perf_counter() - start
            logger.debug("No face detected (%.3fs)", elapsed)
            return {
                "status": "denied",
                "user_id": None,
                "name": None,
                "confidence": None,
                "reason": "No face detected in image",
            }

        # Step 2 – compare with known encodings
        with self._lock:
            known_copy = dict(self._known)

        if not known_copy:
            return {
                "status": "denied",
                "user_id": None,
                "name": None,
                "confidence": None,
                "reason": "No registered users in system",
            }

        user_ids = list(known_copy.keys())
        known_encodings = [known_copy[uid][1] for uid in user_ids]

        # face_recognition.face_distance returns Euclidean distances (lower = closer)
        distances = face_recognition.face_distance(known_encodings, incoming)
        best_idx = int(np.argmin(distances))
        best_distance = float(distances[best_idx])

        # Convert distance to a 0-1 confidence score
        confidence = max(0.0, 1.0 - best_distance)

        elapsed = time.perf_counter() - start
        logger.debug(
            "Recognition complete in %.3fs | best distance=%.4f | confidence=%.4f",
            elapsed, best_distance, confidence,
        )

        # Step 3 – threshold check
        if best_distance <= settings.FACE_DISTANCE_THRESHOLD:
            best_user_id = user_ids[best_idx]
            best_name = known_copy[best_user_id][0]
            return {
                "status": "allowed",
                "user_id": best_user_id,
                "name": best_name,
                "confidence": round(confidence, 4),
                "reason": None,
            }

        return {
            "status": "denied",
            "user_id": None,
            "name": None,
            "confidence": round(confidence, 4),
            "reason": "Unknown person – face not recognised",
        }


# ── Module-level singleton ────────────────────────────────────────────────────
face_service = FaceRecognitionService()
