from backend.app.db.database import SessionLocal
from sqlalchemy import text

def run_validation():
    db = SessionLocal()
    try:
        # Total users
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        
        # Total profiles
        total_profiles = db.execute(text("SELECT COUNT(*) FROM farmer_profiles")).scalar()
        
        # Users without profile
        unmapped_users = db.execute(text(
            "SELECT users.id, users.name, users.email FROM users LEFT JOIN farmer_profiles ON users.id = farmer_profiles.user_id WHERE farmer_profiles.id IS NULL"
        )).fetchall()
        
        print("--- Migration Validation Report ---")
        print(f"Total Users: {total_users}")
        print(f"Total FarmerProfiles: {total_profiles}")
        print(f"Users Without Profile: {len(unmapped_users)}")
        if unmapped_users:
            print("Unmapped Users list:")
            for u in unmapped_users:
                print(f"  ID: {u.id}, Name: {u.name}, Email: {u.email}")
        else:
            print("[SUCCESS] Every user has a corresponding FarmerProfile record.")
            
        # Verify unique constraints and indexes
        phone_index_check = db.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'users' AND indexname = 'ix_users_phone_number'"
        )).fetchone()
        print(f"Index 'ix_users_phone_number' exists: {phone_index_check is not None}")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_validation()
