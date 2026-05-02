"""
Image processing helpers: base64 decoding, format conversion,
size validation, and face crop utilities.
"""

import base64
import io
import logging
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

MAX_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024


def decode_base64_image(b64_string: str) -> np.ndarray:
    """
    Decode a base64-encoded image string to an OpenCV BGR ndarray.

    Accepts both raw base64 and data-URL format:
      data:image/jpeg;base64,/9j/4AAQ...
    """
    # Strip optional data-URL header
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]

    raw_bytes = base64.b64decode(b64_string)

    if len(raw_bytes) > MAX_BYTES:
        raise ValueError(
            f"Image too large ({len(raw_bytes) / 1024 / 1024:.1f} MB). "
            f"Max allowed: {settings.MAX_IMAGE_SIZE_MB} MB."
        )

    # Decode via NumPy / OpenCV
    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Failed to decode image. Ensure it is a valid JPEG or PNG.")

    return img


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert OpenCV BGR image to RGB (required by face_recognition)."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def resize_for_recognition(image: np.ndarray, max_width: int = 640) -> np.ndarray:
    """
    Downscale large images to speed up recognition.
    Maintains aspect ratio.
    """
    h, w = image.shape[:2]
    if w <= max_width:
        return image
    scale = max_width / w
    new_w = max_width
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def encode_image_to_base64(image: np.ndarray, fmt: str = ".jpg") -> str:
    """Encode an OpenCV BGR image to a base64 string."""
    success, buffer = cv2.imencode(fmt, image)
    if not success:
        raise ValueError("Failed to encode image to base64.")
    return base64.b64encode(buffer).decode("utf-8")


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert a PIL Image to an OpenCV BGR ndarray."""
    rgb = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def validate_image_has_face_region(image: np.ndarray) -> bool:
    """
    Quick pre-check using OpenCV Haar cascade before running
    the heavier face_recognition library.
    Returns True if at least one face candidate is found.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0
