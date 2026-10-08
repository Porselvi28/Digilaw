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
    from app.models.evidence import EvidenceAnalysis
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

client = TestClient(app)

def test_legal_relevance_flow():
    print("1. Creating a test case...")
    case_data = {
        "title": "Legal Relevance Test Case",
        "description": "Test case for legal relevance mapping.",
        "legal_domain": "Criminal Law"
    }
    response = client.post("/api/cases", json=case_data)
    assert response.status_code == 201
    created_case = response.json()
    case_id = created_case["id"]
    print(f"Case ID: {case_id}")

    print("\n2. Testing relevance analysis when no evidence exists (should fail)...")
    response = client.post(f"/api/cases/{case_id}/analyze-legal-relevance")
    assert response.status_code == 400
    print(f"Expected failure: {response.json()}")

    print("\n3. Creating mock document and evidence analysis...")
    # Create a dummy file
    dummy_text = "The accused committed theft. The theft occurred in Mumbai."
    file_path = "mock_doc.txt"
    with open(file_path, "w") as f:
        f.write(dummy_text)
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            data={"case_id": case_id},
            files={"file": ("mock_doc.txt", f, "text/plain")}
        )
    assert response.status_code == 201
    document = response.json()
    document_id = document["id"]
    print(f"Document ID: {document_id}")
    
    os.remove(file_path)

    from app.database.connection import SessionLocal
    db = SessionLocal()
    
    # Mark document as extracted
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    db_doc.extracted_text = dummy_text
    db_doc.extraction_status = "completed"
    db.commit()
    db.refresh(db_doc)
    # Create Evidence Analysis
    evidence = EvidenceAnalysis(
        document_id=db_doc.id,
        case_id=case_id,
        status="completed",
        facts={
            "claims_allegations": ["The accused committed theft of 500 rupees."],
            "events": ["The theft occurred in Mumbai."]
        }
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    db.close()
    
    print("Mock evidence created.")

    print("\n4. Testing legal relevance analysis...")
    response = client.post(f"/api/cases/{case_id}/analyze-legal-relevance")
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Generated {len(results)} relevance records.")
        for res in results:
            print(f"- Fact: {res['fact_reference']}")
            print(f"  Source: {res['legal_source']}")
            print(f"  Explanation: {res['relevance_explanation']}")
    else:
        print(f"Failed: {response.json()}")
        assert False

    print("\n5. Testing invalid case ID...")
    response = client.post(f"/api/cases/999999/analyze-legal-relevance")
    assert response.status_code == 400
    print(f"Expected failure: {response.json()}")

    print("\nALL LEGAL RELEVANCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_legal_relevance_flow()
