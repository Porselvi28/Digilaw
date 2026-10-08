import sys
import os
from sqlalchemy import create_engine, text

# Adjust path to find the 'app' module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.connection import engine, SessionLocal
from app.database.base import Base
from app.models.user import User
from app.models.case import Case
from app.services.auth_service import get_password_hash

def migrate():
    print("Starting Auth v1 Migration...")
    
    # 1. Create the 'users' table if it doesn't exist
    print("Creating users table...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Check if the legacy user exists, if not, create it
        legacy_username = "legacy_system_user"
        legacy_email = "legacy@digilaw.local"
        
        legacy_user = db.query(User).filter(User.username == legacy_username).first()
        if not legacy_user:
            print("Creating legacy system user...")
            hashed_pw = get_password_hash("legacy_password_change_me_immediately")
            legacy_user = User(
                username=legacy_username,
                email=legacy_email,
                hashed_password=hashed_pw
            )
            db.add(legacy_user)
            db.commit()
            db.refresh(legacy_user)
            print(f"Legacy user created with ID {legacy_user.id}")
        else:
            print(f"Legacy user already exists with ID {legacy_user.id}")
            
        legacy_user_id = legacy_user.id
        
    finally:
        db.close()
        
    # 3. Add user_id column to cases and migrate existing cases using raw SQL
    print("Migrating cases table...")
    with engine.begin() as conn:
        # Check if user_id column exists
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='cases' AND column_name='user_id'"))
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            print("Adding user_id column to cases...")
            conn.execute(text("ALTER TABLE cases ADD COLUMN user_id INTEGER;"))
            
            print(f"Assigning existing cases to legacy user {legacy_user_id}...")
            conn.execute(text(f"UPDATE cases SET user_id = {legacy_user_id} WHERE user_id IS NULL;"))
            
            print("Enforcing NOT NULL constraint on cases.user_id...")
            conn.execute(text("ALTER TABLE cases ALTER COLUMN user_id SET NOT NULL;"))
            
            print("Adding foreign key constraint...")
            conn.execute(text("ALTER TABLE cases ADD CONSTRAINT fk_cases_user_id FOREIGN KEY (user_id) REFERENCES users(id);"))
            print("Migration successful.")
        else:
            print("Column cases.user_id already exists. Nothing to migrate.")
            
if __name__ == "__main__":
    migrate()
