import sys
from fastapi.testclient import TestClient

try:
    from app.main import app
    "description": "This is a test description for a legal case.",
    "legal_domain": "Corporate Law"
}
response = client.post("/api/cases", json=case_data)
print(f"Create response: {response.status_code} - {response.json()}")
assert response.status_code == 201
created_case = response.json()
case_id = created_case["id"]

print("\n3. Getting all cases...")
response = client.get("/api/cases")
print(f"Get all response: {response.status_code} - {response.json()}")
assert response.status_code == 200
assert len(response.json()) >= 1

print(f"\n4. Getting specific case {case_id}...")
response = client.get(f"/api/cases/{case_id}")
print(f"Get case response: {response.status_code} - {response.json()}")
assert response.status_code == 200
    assert response.json()["title"] == "Test Legal Case via TestClient"

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_client_test()
