from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    scientific_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    ideal_soil = Column(String, nullable=True)
    ideal_season = Column(String, nullable=True)
    water_requirement = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
