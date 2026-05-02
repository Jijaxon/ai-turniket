"""
AI Turniket System – FastAPI Application Entry Point
====================================================
Run with:  uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database.db import engine, SessionLocal, Base
from .services.auth_service import seed_admin_if_needed
from .services.face_recognition_service import face_service
from .routes import auth, users, recognition, logs

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ── Startup / Shutdown lifecycle ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Actions on startup:
    1. Create DB tables
    2. Seed default admin
    3. Load face encodings into memory
    """
    logger.info("🚀 Starting AI Turniket System v%s", settings.APP_VERSION)

    # Create tables (Alembic should be used in production)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_admin_if_needed(db)
        count = face_service.reload_encodings(db)
        logger.info("✅ Face encoding cache loaded: %d entries", count)
    finally:
        db.close()

    yield  # App runs here

    logger.info("🛑 Shutting down AI Turniket System")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered face recognition access control system. "
        "Provides real-time face recognition, user management, "
        "access logging, and admin dashboard APIs."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recognition.router)
app.include_router(logs.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "cached_faces": face_service.get_cache_size(),
    }


@app.get("/", tags=["System"])
def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}
