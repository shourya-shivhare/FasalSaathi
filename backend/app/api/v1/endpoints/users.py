from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/me")
async def get_current_user():
    # TODO: decode JWT, fetch user from DB
    raise HTTPException(status_code=501, detail="Not implemented yet")
