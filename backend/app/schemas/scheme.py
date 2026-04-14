# app/schemas/scheme.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict, Literal
from datetime import datetime


class SchemeBase(BaseModel):
    name: str
    ministry: Optional[str] = None
    category: Optional[Literal["subsidy", "insurance", "loan", "training"]] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[Dict[str, Any]] = None

    # Avoid mutable default
    states: List[str] = Field(default_factory=lambda: ["ALL"])

    crops: Optional[List[str]] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    apply_url: Optional[str] = None


class SchemeCreate(SchemeBase):
    source: str = "manual"


class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    ministry: Optional[str] = None
    category: Optional[Literal["subsidy", "insurance", "loan", "training"]] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    eligibility: Optional[Dict[str, Any]] = None
    states: Optional[List[str]] = None
    crops: Optional[List[str]] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    apply_url: Optional[str] = None


class SchemeOut(SchemeBase):
    id: int
    source: str
    last_synced: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SchemeRecommendation(SchemeOut):
    match_score: float
    matched_on: List[str]