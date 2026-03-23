from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.routers.chat import router as chat_router
from app.routers.crop_advisor import router as crop_advisor_router

app = FastAPI(
    title="FasalSaathi AI Service",
    version="1.0.0",
    description="LangChain + LangGraph powered AI backend for FasalSaathi",
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


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "message": "FasalSaathi AI Service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
