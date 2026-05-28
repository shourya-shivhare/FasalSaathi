"""
FasalSaathi AI Service — Main Application Entry Point
v3.0.0: LangGraph-based multi-agent orchestration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.core.config import settings
from app.routers.chat import router as chat_router
from app.routers.detection import router as detection_router
from app.routers.agents import router as agents_router

# ── Configure logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(
    title="FasalSaathi AI Service",
    version="3.0.0",
    description="LangGraph-based autonomous multi-agent orchestration for Indian agriculture",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
# Primary: unified chat + image upload via LangGraph
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

# Legacy: direct pest detection endpoint (still useful for standalone YOLO)
app.include_router(detection_router, prefix="/detect", tags=["Pest Detection"])

# Agent-specific endpoints (backward-compatible with backend proxy)
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])


# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Clean expired image uploads on startup."""
    try:
        from app.storage.image_store import ImageStore
        store = ImageStore()
        cleaned = await store.cleanup_expired(ttl_hours=24)
        if cleaned:
            logging.getLogger("main").info(
                "🧹 Startup cleanup: removed %d expired images", cleaned
            )
    except Exception as e:
        logging.getLogger("main").warning("Startup cleanup failed: %s", e)


@app.get("/", tags=["Health"])
def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "engine": "LangGraph",
        "message": "FasalSaathi AI Service is running",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
