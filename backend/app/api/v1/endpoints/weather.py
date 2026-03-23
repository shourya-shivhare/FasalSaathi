from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/current")
async def get_current_weather(lat: float, lon: float):
    # TODO: call external weather API
    raise HTTPException(status_code=501, detail="Not implemented yet")
