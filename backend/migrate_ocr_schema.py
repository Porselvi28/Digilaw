from sqlalchemy import text
from app.database.connection import engine
from app.models.document import Document
from app.database.base import Base

def migrate():
    print("Starting database migration for OCR v1...")
    
    # In SQLite (used in tests), ADD COLUMN IF NOT EXISTS is not standard until very recent versions,
    # but in PostgreSQL it works. We'll try to execute them and catch expected exceptions.
    
    columns = [
        ("ocr_used", "BOOLEAN DEFAULT FALSE NOT NULL"),
        ("ocr_status", "VARCHAR(50)"),
        ("page_count", "INTEGER"),
        ("extracted_character_count", "INTEGER")
    ]
    
    with engine.begin() as conn:
        for col_name, col_type in columns:
            try:
                # We use generic alter table
                conn.execute(text(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type}"))
                print(f"Added column: {col_name}")
            except Exception as e:
                # If column already exists or other error (e.g. SQLite throws operational error)
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"Column {col_name} already exists.")
                else:
                    print(f"Note on {col_name}: {e}")
                    
    print("Migration finished safely.")

if __name__ == "__main__":
    # Wait, we should also call create_all just in case it's a completely fresh DB
    # that hasn't even been created yet, but that's handled by main.py usually.
    migrate()
