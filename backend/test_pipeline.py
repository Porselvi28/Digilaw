import sys
import os
import json
from unittest.mock import patch, MagicMock

# --- MOCK BROKEN TORCH DUE TO MAX_PATH ISSUE ---
mock_torch = MagicMock()
mock_st = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch._C'] = mock_torch
sys.modules['sentence_transformers'] = mock_st
sys.modules['sentence_transformers.backend'] = mock_st
sys.modules['sentence_transformers.backend.load'] = mock_st

mock_st_instance = MagicMock()
mock_st_instance.encode.return_value.tolist.return_value = [0.1] * 384
mock_st.SentenceTransformer.return_value = mock_st_instance

sys.modules['transformers'] = MagicMock()
sys.modules['transformers.configuration_utils'] = MagicMock()
sys.modules['transformers.generation'] = MagicMock()
sys.modules['transformers.generation.configuration_utils'] = MagicMock()
sys.modules['transformers.generation.logits_process'] = MagicMock()
# -----------------------------------------------

os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["GEMINI_API_KEY"] = "dummy_key"

from sqlalchemy import text
from app.database.connection import engine, SessionLocal
from fastapi.testclient import TestClient
from app.main import app as main_app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

main_app.dependency_overrides[get_current_active_user] = override_get_current_active_user

# --- MOCK GEMINI CALLS ---
class MockGeminiResponse:
    def __init__(self, text):
        self.text = text

mock_gemini = MagicMock()
def mock_generate_content(model, contents, **kwargs):
    prompt = str(contents).lower()
    if "analyze the following evidence fact against the provided legal context" in prompt:
        return MockGeminiResponse(json.dumps(
            {"legal_source": "Contract Act", "act_judgment_info": "10", "relevance_explanation": "Valid contract requirements.", "relevance_score": 9}
        ))
    elif "extract key factual evidence" in prompt:
        return MockGeminiResponse(json.dumps({
            "people_roles": ["John Doe"],
            "organizations": ["DigiLaw Inc"],
            "dates": ["2023-01-01"],
            "locations": ["New York"],
            "events": ["Signed a contract"],
            "monetary_amounts": ["$10,000"],
            "claims_allegations": ["Breach of contract"],
            "important_statements": ["The contract is valid."],
            "document_type_purpose": "Contract"
        }))
    elif "determine if there are any missing documents" in prompt:
        return MockGeminiResponse(json.dumps([
            {"document_category": "Financial", "document_name": "Invoice", "requirement_level": "required", "reason": "Proof of payment."}
        ]))
    elif "how the retrieved authoritative judgments are similar or relevant" in prompt:
        return MockGeminiResponse(json.dumps([
            {"judgment_title": "Smith v Jones", "similarity_explanation": "Both involve breach."}
        ]))
    else:
        return MockGeminiResponse(json.dumps([
            {"action_title": "Review contract", "description": "Check validity.", "priority": "High", "sequence_order": 1, "action_category": "Review", "rationale": "Need validity"}
        ]))
        
mock_gemini.models.generate_content.side_effect = mock_generate_content

def run_tests():
    print("Initializing TestClient for Pipeline Tests...")
    client = TestClient(main_app)
    
    # We will mock the gemini client inside the app services
    import app.services.rag_service
    app.services.rag_service.gemini_client.models.generate_content = mock_gemini.models.generate_content
    
    tests_passed = []
    tests_failed = []

    def check(test_name, condition, error_msg=""):
        if condition:
            print(f"[PASS] {test_name}")
            tests_passed.append(test_name)
        else:
            print(f"[FAIL] {test_name} - {error_msg}")
            tests_failed.append(test_name)

    try:
        print("\n--- Testing Pipeline Creation ---")
        res = client.post("/api/cases", json={
            "title": "Pipeline Integration Case",
            "description": "Full E2E test for the new pipeline endpoint.",
            "legal_domain": "Contracts"
        })
        case_id = res.json()["id"]
        check("Case created", res.status_code == 201)

        # Upload a dummy TXT document
        test_txt_content = b"This is a contract signed by John Doe in New York on 2023-01-01 for $10,000."
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("contract.txt", test_txt_content, "text/plain")}
        )
        check("Document uploaded", res.status_code == 201)

        print("\n--- Running Full Pipeline ---")
        res = client.post(f"/api/cases/{case_id}/run-pipeline")
        
        check("Pipeline executed successfully (200 OK)", res.status_code == 200, f"Status: {res.status_code}, Response: {res.text}")
        
        if res.status_code == 200:
            data = res.json()
            check("Overall status is completed", data.get("overall_status") == "completed", f"Status: {data.get('overall_status')}")
            check("Document extraction completed", data["document_extraction"]["status"] == "completed")
            check("Evidence analysis completed", data["evidence_analysis"]["status"] == "completed")
            check("Legal relevance completed", data["legal_relevance"]["status"] == "completed")
            check("Missing documents completed", data["missing_documents"]["status"] == "completed")
            check("Similar cases completed", data["similar_cases"]["status"] == "completed")
            check("Action plan completed", data["action_plan"]["status"] == "completed")
            
            # Verify database records
            from app.models.evidence import EvidenceAnalysis
            from app.models.relevance import LegalRelevanceAnalysis
            from app.models.missing_document import MissingDocumentRecommendation
            from app.models.similar_case import SimilarCase
            from app.models.action_plan import ActionPlan
            db = SessionLocal()
            try:
                evidence = db.query(EvidenceAnalysis).filter(EvidenceAnalysis.case_id == case_id).all()
                check("Evidence records exist in DB", len(evidence) == 1)
                
                relevance = db.query(LegalRelevanceAnalysis).filter(LegalRelevanceAnalysis.case_id == case_id).all()
                check("Legal Relevance records exist in DB", len(relevance) > 0)
                
                missing_docs = db.query(MissingDocumentRecommendation).filter(MissingDocumentRecommendation.case_id == case_id).all()
                check("Missing Docs records exist in DB", len(missing_docs) > 0)
                
                similar_cases = db.query(SimilarCase).filter(SimilarCase.case_id == case_id).all()
                check("Similar Cases records exist in DB", len(similar_cases) > 0)
                
                action_plan = db.query(ActionPlan).filter(ActionPlan.case_id == case_id).all()
                check("Action Plan records exist in DB", len(action_plan) > 0)
            finally:
                db.close()

        print("\n--- Running Full Pipeline Again (Idempotency) ---")
        res = client.post(f"/api/cases/{case_id}/run-pipeline")
        check("Pipeline re-executed successfully (200 OK)", res.status_code == 200, f"Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            check("Overall status is completed on re-run", data.get("overall_status") == "completed")
            
            # Check DB again to ensure no duplicate spam (specifically relevance, missing docs, similar cases, action plans which delete/recreate)
            db = SessionLocal()
            try:
                # Should still be just 1 (or same number as before) because they are replaced
                relevance2 = db.query(LegalRelevanceAnalysis).filter(LegalRelevanceAnalysis.case_id == case_id).all()
                check("Legal Relevance count is stable on re-run", len(relevance2) == len(relevance))
            finally:
                db.close()

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Exception during tests: {e}")

    print("\n--- TEST SUMMARY ---")
    print(f"Passed: {len(tests_passed)}")
    print(f"Failed: {len(tests_failed)}")
    for f in tests_failed:
        print(f"  - {f}")

if __name__ == "__main__":
    run_tests()
