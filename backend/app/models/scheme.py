# app/models/scheme.py
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.types import TypeDecorator, TEXT
from backend.app.db.database import Base


class SafeArray(TypeDecorator):
    """Fallback type for SQLite when Postgres ARRAY is not supported."""
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(String))
        return dialect.type_descriptor(TEXT)

    def process_bind_param(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        if dialect.name == "postgresql":
            return value
        if value is not None:
            try:
                return json.loads(value)
            except Exception:
                return []
        return []


class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    ministry = Column(String)
    category = Column(String, index=True)        # subsidy, insurance, loan, training
    description = Column(Text)
    benefits = Column(Text)
    eligibility = Column(JSON) if hasattr(Base, "metadata") else Column(Text)
    states = Column(SafeArray())               # ["ALL"] or ["MH","UP"]
    crops = Column(SafeArray(), nullable=True) # ["wheat","rice"] or null = any
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    apply_url = Column(String)
    source = Column(String)                      # "myscheme" / "data.gov.in" / "manual"
    last_synced = Column(DateTime)
