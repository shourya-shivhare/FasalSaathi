from pydantic import BaseModel
from typing import Optional

class CropBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    ideal_soil: Optional[str] = None
    ideal_season: Optional[str] = None
    water_requirement: Optional[str] = None
    image_url: Optional[str] = None

class CropCreate(CropBase):
    pass

class CropUpdate(CropBase):
    pass

class CropInDBBase(CropBase):
    id: int

    class Config:
        from_attributes = True

class Crop(CropInDBBase):
    pass
