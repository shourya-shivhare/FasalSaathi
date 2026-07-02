from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

# If it's a synchronous app, we use regular create_engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def upgrade_db_schema(db_engine):
    """
    Programmatic schema upgrade helper for SQLite / PostgreSQL.
    Checks and adds any newly defined columns to existing tables.
    """
    inspector = inspect(db_engine)
    
    # 1. Update 'farms' table
    if "farms" in inspector.get_table_names():
        farm_cols = [c["name"] for c in inspector.get_columns("farms")]
        new_farm_cols = {
            "latitude": "FLOAT",
            "longitude": "FLOAT",
            "ph": "FLOAT",
            "nitrogen": "FLOAT",
            "phosphorus": "FLOAT",
            "potassium": "FLOAT",
            "organic_carbon": "FLOAT"
        }
        with db_engine.begin() as conn:
            for col_name, col_type in new_farm_cols.items():
                if col_name not in farm_cols:
                    conn.execute(text(f"ALTER TABLE farms ADD COLUMN {col_name} {col_type}"))

    # 2. Update 'farmer_profiles' table
    if "farmer_profiles" in inspector.get_table_names():
        profile_cols = [c["name"] for c in inspector.get_columns("farmer_profiles")]
        new_profile_cols = {
            "market_preferences": "JSON",
            "scheme_participation": "JSON"
        }
        with db_engine.begin() as conn:
            for col_name, col_type in new_profile_cols.items():
                if col_name not in profile_cols:
                    conn.execute(text(f"ALTER TABLE farmer_profiles ADD COLUMN {col_name} {col_type}"))

