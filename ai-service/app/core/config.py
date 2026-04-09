from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # LLM
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.3

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",   # FastAPI backend
        "http://localhost:5173",   # Vite frontend (for direct dev access)
    ]

    # Vector store / embeddings
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "models/embedding-001"

    # Memory
    MAX_HISTORY_LENGTH: int = 10

    # YOLO Pest Detection
    YOLO_WEIGHTS_PATH: str = "models/best.pt"
    YOLO_CONF_THRESHOLD: float = 0.35
    YOLO_OUTPUT_DIR: str = "outputs/detections"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
