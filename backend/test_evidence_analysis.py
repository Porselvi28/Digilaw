import sys
import json
import uuid
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from app.main import app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    from app.database.connection import get_db, engine
    from app.database.base import Base
    from app.models.case import Case
    from app.models.document import Document
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

client = TestClient(app)

# We'll use the main DB but create a test case to work with
def test_evidence_analysis_flow():
    print("1. Creating a test case...")
    case_data = {
        "title": "Evidence Test Case",
        "description": "This is a test description for evidence analysis.",
        "legal_domain": "Test Law"
    }
    response = client.post("/api/cases", json=case_data)
    assert response.status_code == 201
    created_case = response.json()
    case_id = created_case["id"]
    print(f"Case ID: {case_id}")

    print("\n2. Uploading a test document...")
    # Create a dummy file
    dummy_text = "This is a test document. John Doe is the plaintiff. He claims 500 dollars. ABC Corp is the defendant. Date of incident: 2023-01-01 in New York."
    file_path = "test_doc.txt"
    with open(file_path, "w") as f:
        f.write(dummy_text)
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            data={"case_id": case_id},
            files={"file": ("test_doc.txt", f, "text/plain")}
        )
    assert response.status_code == 201
    document = response.json()
    document_id = document["id"]
    print(f"Document ID: {document_id}")
    
    # Cleanup dummy file
    os.remove(file_path)

    print("\n3. Testing evidence extraction on unextracted document (should fail)...")
    response = client.post(f"/api/documents/{document_id}/analyze-evidence")
    assert response.status_code == 400
    print(f"Expected failure: {response.json()}")

    print("\n4. Simulating text extraction...")
    # Since we don't have OCR/extract setup for simple tests, we mock the DB state directly
    from app.database.connection import SessionLocal
    db = SessionLocal()
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    db_doc.extracted_text = dummy_text
    db_doc.extraction_status = "completed"
    db.commit()
    db.close()
    print("Document text marked as extracted.")

    print("\n5. Testing evidence extraction on extracted document...")
    response = client.post(f"/api/documents/{document_id}/analyze-evidence")
    print(f"Analysis response status: {response.status_code}")
    print(f"Analysis response body: {response.json()}")
    assert response.status_code == 200
    analysis = response.json()
    assert analysis["status"] == "completed"
    assert "John Doe" in str(analysis["facts"])
    
    print("\n6. Testing invalid document ID...")
    response = client.post(f"/api/documents/999999/analyze-evidence")
    assert response.status_code == 404
    print(f"Expected failure: {response.json()}")
    
    print("\nALL EVIDENCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_evidence_analysis_flow()
