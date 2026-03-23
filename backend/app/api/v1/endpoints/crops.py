from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def list_crops():
    # TODO: return crop list from DB
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{crop_id}")
async def get_crop(crop_id: int):
    raise HTTPException(status_code=501, detail="Not implemented yet")
