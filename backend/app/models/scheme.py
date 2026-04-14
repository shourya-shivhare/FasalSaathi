# app/models/scheme.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from app.db.database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    ministry = Column(String)
    category = Column(String, index=True)        # subsidy, insurance, loan, training
    description = Column(Text)
    benefits = Column(Text)
    eligibility = Column(JSON)                   # structured rules (see below)
    states = Column(ARRAY(String))               # ["ALL"] or ["MH","UP"]
    crops = Column(ARRAY(String), nullable=True) # ["wheat","rice"] or null = any
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    apply_url = Column(String)
    source = Column(String)                      # "myscheme" / "data.gov.in" / "manual"
    last_synced = Column(DateTime)
