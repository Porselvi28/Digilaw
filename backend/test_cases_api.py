import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys

print("Starting Uvicorn server...")
proc = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8125"])

time.sleep(10)  # Wait for HF models to load

try:
    # 1. Check health
    health_req = urllib.request.urlopen("http://localhost:8125/api/health")
    print(f"Health response: {health_req.read().decode()}")

    # 2. Create case
    case_data = {
        "title": "Test Legal Case",
        "description": "This is a test description for a legal case.",
        "legal_domain": "Corporate Law"
    }
    req = urllib.request.Request(
        "http://localhost:8125/api/cases",
        data=json.dumps(case_data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    res = urllib.request.urlopen(req)
    created_case = json.loads(res.read().decode())
    print(f"Created Case: {created_case}")
    
    case_id = created_case["id"]

    # 3. Get all cases
    req2 = urllib.request.Request("http://localhost:8125/api/cases")
    res2 = urllib.request.urlopen(req2)
    all_cases = json.loads(res2.read().decode())
    print(f"All cases count: {len(all_cases)}")
    assert len(all_cases) >= 1

    # 4. Get specific case
    req3 = urllib.request.Request(f"http://localhost:8125/api/cases/{case_id}")
    res3 = urllib.request.urlopen(req3)
    fetched_case = json.loads(res3.read().decode())
    print(f"Fetched Case: {fetched_case}")
    assert fetched_case["title"] == "Test Legal Case"
    
    print("ALL TESTS PASSED SUCCESSFULLY!")

except Exception as e:
    print(f"Error during testing: {e}")
    sys.exit(1)
finally:
    proc.terminate()
    proc.wait()
