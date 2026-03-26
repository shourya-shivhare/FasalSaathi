from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, crops, weather, chat, detect

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(crops.router, prefix="/crops", tags=["Crops"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat / AI"])
api_router.include_router(detect.router, prefix="", tags=["Pest Detection"])
