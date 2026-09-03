import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB", "digilaw_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

def run_migration():
    print("Connecting to database...")
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Check if column exists before adding it
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='extracted_text'")
                if not cur.fetchone():
                    print("Adding extracted_text column...")
                    cur.execute("ALTER TABLE documents ADD COLUMN extracted_text TEXT;")
                else:
                    print("Column extracted_text already exists.")

                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='extraction_status'")
                if not cur.fetchone():
                    print("Adding extraction_status column...")
                    cur.execute("ALTER TABLE documents ADD COLUMN extraction_status VARCHAR(50) DEFAULT 'pending';")
                else:
                    print("Column extraction_status already exists.")

                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='extraction_error'")
                if not cur.fetchone():
                    print("Adding extraction_error column...")
                    cur.execute("ALTER TABLE documents ADD COLUMN extraction_error TEXT;")
                else:
                    print("Column extraction_error already exists.")
            
            conn.commit()
            print("Migration completed successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migration()
