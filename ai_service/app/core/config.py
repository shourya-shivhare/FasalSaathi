from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # LLM
    GOOGLE_API_KEY: str = ""
    GOOGLE_API_KEYS: str = ""        # Comma-separated list of API keys for rotation
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

    # Data.gov.in API
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_RESOURCE_ID: str = ""

    # Market Intelligence APIs
    AGMARKNET_API_KEY: str = ""
    AGMARKNET_BASE_URL: str = "https://api.data.gov.in"
    AGMARKNET_RESOURCE_ID: str = "9ef84268-d588-465a-a308-a864a43d0070"
    OPENWEATHER_API_KEY: str = ""
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    MARKET_CACHE_TTL_SECONDS: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
