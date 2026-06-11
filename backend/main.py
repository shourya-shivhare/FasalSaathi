from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import sys
import uvicorn

try:
    from ai_service.infer import load_model
except ImportError:
    load_model = None

from backend.app.core.config import settings
from backend.app.api.v1.router import api_router

#database properites
from backend.app.db.database import Base, engine
from backend.app.models import user, crop, farm, crop_cycle, crop_journal, pest_detection_history, notification

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warmup YOLO model
    if load_model:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        weights_path = PROJECT_ROOT / "ai_service" / "models" / "best.pt"
        if weights_path.exists():
            print(f"[*] Warming up YOLO model from {weights_path}...")
            load_model(weights_path)
            print("[*] YOLO model warmed up successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FasalSaathi Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

#creating tables of all the defined models 
Base.metadata.create_all(bind=engine)

# Mount static directory for annotated images
# The outputs directory is at the root FasalSaathi/outputs
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure the directory exists to avoid startup errors
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(OUTPUTS_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "FasalSaathi Backend is running"}


if __name__ == "__main__":
    # Ensure it can be run via python -m backend.main from project root
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
