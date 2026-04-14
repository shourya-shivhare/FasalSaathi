from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.routers.chat import router as chat_router
from app.routers.crop_advisor import router as crop_advisor_router
from app.routers.orchestrator_router import router as orchestrator_router

app = FastAPI(
    title="FasalSaathi AI Service",
    version="2.0.0",
    description="LangChain + LangGraph powered AI backend for FasalSaathi — Multi-Agent Architecture",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(crop_advisor_router, prefix="/api/crop-advisor", tags=["Crop Advisor"])
app.include_router(orchestrator_router, prefix="/api/v1/agents", tags=["Agents & Orchestrator"])



@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "FasalSaathi AI Service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
