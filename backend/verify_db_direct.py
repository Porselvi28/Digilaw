import sys
from app.database.connection import engine
from sqlalchemy import text

def check_db():
    print("Checking database directly...")
    try:
        from app.main import app  # This will trigger DB initialization
        print("Imported main successfully.")
    except Exception as e:
        print(f"Error importing main: {e}")
        sys.exit(1)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
        tables = [row[0] for row in result]
        print(f"Tables in database: {tables}")
        if "cases" in tables:
            print("SUCCESS: 'cases' table found in database.")
        else:
            print("ERROR: 'cases' table NOT found in database.")

if __name__ == "__main__":
    check_db()
