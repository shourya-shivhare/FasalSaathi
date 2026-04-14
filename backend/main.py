from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router

#database properites
from app.db.database import Base, engine
from app.models import user, crop # change this based on models 

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FasalSaathi Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

#creating tables of all the defined models 
Base.metadata.create_all(bind=engine)

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
