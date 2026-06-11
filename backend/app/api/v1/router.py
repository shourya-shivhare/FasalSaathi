from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth, users, crops, weather, chat, detect, schemes, agents, market,
    farms, crop_cycles, journal, pest_history, notifications, admin
)

api_router = APIRouter()

api_router.include_router(auth.router,          prefix="/auth",          tags=["Auth"])
api_router.include_router(users.router,         prefix="/users",         tags=["Users"])
api_router.include_router(admin.router,         prefix="/admin",         tags=["Admin"])
api_router.include_router(crops.router,         prefix="/crops",         tags=["Crops"])
api_router.include_router(weather.router,       prefix="/weather",       tags=["Weather"])
api_router.include_router(chat.router,          prefix="/chat",          tags=["Chat / AI"])
api_router.include_router(detect.router,        prefix="/detect",        tags=["Pest Detection"])
api_router.include_router(schemes.router,       prefix="/schemes",       tags=["Schemes"])
api_router.include_router(agents.router,        prefix="/agents",        tags=["AI Agents"])
api_router.include_router(market.router,        prefix="/market",        tags=["Market"])
api_router.include_router(farms.router,         prefix="/farms",         tags=["Farms"])
api_router.include_router(crop_cycles.router,   prefix="/crop-cycles",   tags=["Crop Cycles"])
api_router.include_router(journal.router,       prefix="/journal",       tags=["Journal"])
api_router.include_router(pest_history.router,  prefix="/pest-history",  tags=["Pest History"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])


