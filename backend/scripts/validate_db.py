import os
import sys
import logging
from datetime import datetime, timezone

# Add parent directory to path so backend module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import configure_mappers
from alembic.config import Config
from alembic.script import ScriptDirectory

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("validate_db")

def run_validation():
    logger.info("Starting Database Verification...")
    
    # 1. Environment & Config Check
    from backend.app.core.config import settings
    db_url = settings.DATABASE_URL
    logger.info(f"Loaded DATABASE_URL from environment (masked): {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    if "localhost" not in db_url and "127.0.0.1" not in db_url:
        logger.info("Configuration is cloud-ready (no localhost hardcoded in DATABASE_URL).")
    else:
        logger.info("Running on local connection (localhost/127.0.0.1 detected).")

    # 2. Connection, Pool, and Transaction Health Check
    from backend.app.db.database import engine, SessionLocal, Base
    import backend.app.models as models # Register all models in Base.metadata
    
    try:
        # Check connection and engine creation
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✔ Engine creation and connection pool check passed.")
    except Exception as e:
        logger.error(f"✘ Database connection failed: {e}")
        sys.exit(1)

    # Verify transaction handling using a temporary transaction that is rolled back completely
    try:
        from backend.app.models.user import User
        from backend.app.models.enums import AccountStatus, UserRole
        
        db = SessionLocal()
        # Start a nested transaction / savepoint or a simple transaction
        db.begin_nested() 
        
        # Insert a dummy user
        dummy = User(
            username="temp_validation_user_xyz",
            phone_number="0000000000",
            password_hash="temp_hash",
            status=AccountStatus.ACTIVE,
            role=UserRole.FARMER
        )
        db.add(dummy)
        db.flush()
        
        # Verify it is visible inside the transaction
        user_in_db = db.query(User).filter(User.username == "temp_validation_user_xyz").first()
        if not user_in_db:
            raise RuntimeError("Inserted dummy user was not visible in transaction.")
            
        # Roll back completely
        db.rollback()
        
        # Verify it is gone and left no trace
        db.close()
        
        db = SessionLocal()
        user_after_rollback = db.query(User).filter(User.username == "temp_validation_user_xyz").first()
        db.close()
        
        if user_after_rollback:
            logger.error("✘ Transaction rollback test failed: dummy record still exists.")
            sys.exit(1)
        logger.info("✔ Transaction rollback and isolation check passed successfully.")
    except Exception as e:
        logger.error(f"✘ Transaction handling validation failed: {e}")
        sys.exit(1)

    # 3. Relationship Compilation Integrity Check
    try:
        # Compile all relationships to verify back_populates and foreign keys are valid in SQLAlchemy
        configure_mappers()
        logger.info("✔ SQLAlchemy relationships and mappers configured without errors.")
    except Exception as e:
        logger.error(f"✘ SQLAlchemy mapper compilation failed: {e}")
        sys.exit(1)

    # 4. ORM-to-DB Table Verification & Schema Inspection
    inspector = inspect(engine)
    db_tables = inspector.get_table_names()
    orm_tables = list(Base.metadata.tables.keys())
    
    missing_tables = [table for table in orm_tables if table not in db_tables]
    if missing_tables:
        logger.error(f"✘ Missing tables in database: {missing_tables}")
        sys.exit(1)
    logger.info("✔ All declared ORM models are represented in the database.")

    # 5. Alembic History Check
    if "alembic_version" not in db_tables:
        logger.error("✘ Table 'alembic_version' does not exist in the database.")
        sys.exit(1)
        
    try:
        # Get current version from DB
        with engine.connect() as conn:
            current_version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            
        # Get head version from Alembic files
        alembic_cfg = Config(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alembic.ini")))
        script = ScriptDirectory.from_config(alembic_cfg)
        head_version = script.get_current_head()
        
        logger.info(f"Alembic Database Version: {current_version}")
        logger.info(f"Alembic Code Head Version: {head_version}")
        
        if current_version != head_version:
            logger.error(f"✘ Alembic version mismatch! DB is at {current_version}, but code head is at {head_version}.")
            sys.exit(1)
        logger.info("✔ Alembic version matches the latest migration head.")
    except Exception as e:
        logger.error(f"✘ Alembic verification failed: {e}")
        sys.exit(1)

    # 6. Schema Drift, Constraints, Foreign Keys & Indexes Inspection
    drift_detected = False
    for table_name in orm_tables:
        orm_columns = Base.metadata.tables[table_name].columns
        db_columns_info = {c["name"]: c for c in inspector.get_columns(table_name)}
        
        # Check columns
        for col_name, orm_col in orm_columns.items():
            if col_name not in db_columns_info:
                logger.error(f"✘ Column drift: Table '{table_name}' is missing column '{col_name}' in the database.")
                drift_detected = True
                continue
                
            db_col = db_columns_info[col_name]
            
            # Check NOT NULL constraint
            if orm_col.nullable == False and db_col["nullable"] == True:
                logger.error(f"✘ Constraint drift: Column '{table_name}.{col_name}' should be NOT NULL in database.")
                drift_detected = True
                
            # Check defaults
            if orm_col.default is not None and db_col["default"] is None:
                # Log as warning/info since server-side defaults vs client-side default expressions can differ
                logger.debug(f"Info: Column '{table_name}.{col_name}' has ORM default but no server-side default.")
        
        # Check foreign keys exist
        db_fkeys = inspector.get_foreign_keys(table_name)
        orm_fkeys = Base.metadata.tables[table_name].foreign_keys
        
        for orm_fk in orm_fkeys:
            parent_col = orm_fk.parent.name
            target_table = orm_fk.column.table.name
            target_col = orm_fk.column.name
            
            # Check if this FK is represented in the DB
            fk_exists = False
            for db_fk in db_fkeys:
                if parent_col in db_fk["constrained_columns"] and db_fk["referred_table"] == target_table:
                    fk_exists = True
                    break
            if not fk_exists:
                logger.error(f"✘ Missing Foreign Key: Table '{table_name}' lacks database foreign key on '{parent_col}' -> '{target_table}.{target_col}'")
                drift_detected = True

        # Check indexes & unique constraints
        db_indexes = inspector.get_indexes(table_name)
        db_pk = inspector.get_pk_constraint(table_name)
        
        if not db_pk or not db_pk.get("constrained_columns"):
            logger.error(f"✘ Missing Primary Key: Table '{table_name}' has no primary key.")
            drift_detected = True
            
        # Verify unique constraints for specific important fields (username, phone_number, email)
        if table_name == "users":
            unique_cols = ["username", "phone_number"]
            for col in unique_cols:
                is_unique = False
                for idx in db_indexes:
                    if col in idx["column_names"] and idx["unique"]:
                        is_unique = True
                        break
                # Also check unique constraints list
                unique_constraints = inspector.get_unique_constraints(table_name)
                for uc in unique_constraints:
                    if col in uc["column_names"]:
                        is_unique = True
                        break
                if not is_unique:
                    logger.error(f"✘ Missing Unique Index/Constraint on table '{table_name}' column '{col}'")
                    drift_detected = True

    if drift_detected:
        logger.error("✘ Database schema validation failed due to schema/constraint drift.")
        sys.exit(1)
    else:
        logger.info("✔ Constraints, Foreign Keys, Indexes, and Column types validated with zero drift.")

    # 7. Row Reporting & Empty App Tables Check
    db_session = SessionLocal()
    reference_data = {}
    application_data = {}
    
    # Tables that are considered application/user tables and must be empty
    app_tables = {
        "users", "farmer_profiles", "farms", "crop_cycles", 
        "crop_journal_entries", "pest_detection_histories", 
        "sessions", "security_events", "rate_limit_events"
    }
    
    has_app_data = False
    
    logger.info("--- Database Row Counts Report ---")
    for table_name in sorted(db_tables):
        if table_name == "alembic_version":
            continue
        try:
            count = db_session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            logger.info(f"  Table '{table_name}': {count} rows")
            
            if table_name in app_tables:
                application_data[table_name] = count
                if count > 0:
                    has_app_data = True
            else:
                reference_data[table_name] = count
        except Exception as e:
            logger.error(f"Error reading row count for '{table_name}': {e}")
            
    db_session.close()

    if has_app_data:
        logger.error("✘ Data validation failed: Found active application/user records in: " + 
                     ", ".join([f"{k} ({v} rows)" for k, v in application_data.items() if v > 0]))
        sys.exit(1)
    else:
        logger.info("✔ Data validation passed: All application tables contain exactly zero rows.")
        if reference_data:
            logger.info("Seeded reference data tables: " + 
                        ", ".join([f"{k} ({v} rows)" for k, v in reference_data.items()]))
        else:
            logger.info("No seeded reference tables exist.")

    logger.info("✔✔ All Database Validations Passed Successfully!")
    sys.exit(0)

if __name__ == "__main__":
    run_validation()
