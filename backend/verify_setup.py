import urllib.request
import time
import subprocess
import os

print("Starting Uvicorn server...")
proc = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8123"])

time.sleep(3)

try:
    response = urllib.request.urlopen("http://localhost:8123/api/health")
    print(f"Health response: {response.read().decode('utf-8')}")

    from app.database.connection import engine
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
        tables = [row[0] for row in result]
        print(f"Tables in database: {tables}")
        if "cases" in tables:
            print("SUCCESS: 'cases' table found in database.")
        else:
            print("ERROR: 'cases' table NOT found in database.")
finally:
    proc.terminate()
    proc.wait()
