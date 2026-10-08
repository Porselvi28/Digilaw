import sys
import os
import json
from fastapi.testclient import TestClient

try:
    from app.main import app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    from app.database.connection import SessionLocal
    from app.models.document import Document
    from app.models.evidence import EvidenceAnalysis
    from app.models.relevance import LegalRelevanceAnalysis
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

client = TestClient(app)

def test_missing_documents_flow():
    print("1. Creating a test case...")
    case_data = {
        "title": "Missing Documents Test Case",
        "description": "Test case for missing document detection.",
        "legal_domain": "Criminal Law"
    }
    response = client.post("/api/cases", json=case_data)
    assert response.status_code == 201
    created_case = response.json()
    case_id = created_case["id"]
    print(f"Case ID: {case_id}")

    print("\n2. Testing detection when no documents or evidence exist (baseline)...")
    response = client.post(f"/api/cases/{case_id}/detect-missing-documents")
    assert response.status_code == 200
    results = response.json()
    print(f"Generated {len(results)} baseline recommendations.")
    
    print("\n3. Uploading a mock document to test exclusion...")
    dummy_text = "The accused committed theft. The theft occurred in Mumbai."
    file_path = "FIR_copy.txt"
    with open(file_path, "w") as f:
        f.write(dummy_text)
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/documents/upload",
            data={"case_id": case_id},
            files={"file": ("FIR_copy.txt", f, "text/plain")}
        )
    assert response.status_code == 201
    document = response.json()
    document_id = document["id"]
    os.remove(file_path)
    print(f"Uploaded Document ID: {document_id}")

    print("\n4. Mocking evidence and legal relevance...")
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
    
    # Create Legal Relevance Analysis
    relevance = LegalRelevanceAnalysis(
        case_id=case_id,
        evidence_id=evidence.id,
        fact_reference="The accused committed theft of 500 rupees.",
        legal_source="Bharatiya Nagarik Suraksha Sanhita, 2023 - Section 283",
        relevance_explanation="Section 283 allows summary trial for theft under 20k rupees.",
        relevance_score=8,
        status="completed"
    )
    db.add(relevance)
    db.commit()
    db.close()
    
    print("Mock evidence and relevance created.")

    print("\n5. Testing detection with existing docs, evidence, and relevance...")
    response = client.post(f"/api/cases/{case_id}/detect-missing-documents")
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Generated {len(results)} recommendations.")
        for res in results:
            print(f"- Category: {res['document_category']}")
            print(f"  Name: {res['document_name']}")
            print(f"  Requirement: {res['requirement_level']}")
            print(f"  Reason: {res['reason']}")
            if res['related_legal_source']:
                print(f"  Legal Source: {res['related_legal_source']}")
                
            # Verify the uploaded document is not recommended
            assert "FIR" not in res['document_name'].upper()
    else:
        print(f"Failed: {response.json()}")
        assert False

    print("\n6. Testing retrieval of existing recommendations...")
    response = client.get(f"/api/cases/{case_id}/missing-documents")
    assert response.status_code == 200
    retrieved_results = response.json()
    assert len(retrieved_results) == len(results)
    print("Retrieval successful.")

    print("\n7. Testing invalid case ID...")
    response = client.post(f"/api/cases/999999/detect-missing-documents")
    assert response.status_code == 400
    
    response = client.get(f"/api/cases/999999/missing-documents")
    assert response.status_code == 404
    print("Invalid case ID handled correctly.")

    print("\nALL MISSING DOCUMENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_missing_documents_flow()
