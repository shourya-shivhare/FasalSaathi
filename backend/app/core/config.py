from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "FasalSaathi"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str 

    # Security
    SECRET_KEY: str = "changeme-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes for production-grade security
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # 7 days rotation window

    # Twilio Verify
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_VERIFY_SERVICE_SID: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
    ]

    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"

    # Rate Limiting
    ENABLE_RATE_LIMIT: bool = True

    class Config:
        import os
        from pathlib import Path
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        case_sensitive = True


settings = Settings()
