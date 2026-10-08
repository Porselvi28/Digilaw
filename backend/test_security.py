import sys
import os
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["GEMINI_API_KEY"] = "dummy_key"
from unittest.mock import patch, MagicMock

# --- MOCK BROKEN TORCH DUE TO MAX_PATH ISSUE ---
mock_torch = MagicMock()
mock_st = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch._C'] = mock_torch
sys.modules['sentence_transformers'] = mock_st
sys.modules['sentence_transformers.backend'] = mock_st
sys.modules['sentence_transformers.backend.load'] = mock_st
sys.modules['transformers'] = MagicMock()
sys.modules['transformers.configuration_utils'] = MagicMock()
sys.modules['transformers.generation'] = MagicMock()
sys.modules['transformers.generation.configuration_utils'] = MagicMock()
sys.modules['transformers.generation.logits_process'] = MagicMock()
# -----------------------------------------------

from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

def run_tests():
    print("Initializing TestClient for Security Tests...")
    client = TestClient(app)
    
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
        print("\n--- Testing CORS ---")
        res = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        check("CORS headers present", "access-control-allow-origin" in res.headers, f"Headers: {res.headers}")
        if "access-control-allow-origin" in res.headers:
            check("CORS origin matched", res.headers["access-control-allow-origin"] == "http://localhost:3000", f"Origin: {res.headers['access-control-allow-origin']}")

        print("\n--- Testing Unauthorized Access ---")
        # Remove dependency override temporarily to test real auth
        app.dependency_overrides.pop(get_current_active_user, None)
        res = client.get("/api/cases")
        check("Unauthorized access blocked (401)", res.status_code == 401, f"Status: {res.status_code}")
        
        # Restore override for further tests
        app.dependency_overrides[get_current_active_user] = override_get_current_active_user

        print("\n--- Testing Error Leakage ---")
        # Create a dummy case first
        res = client.post("/api/cases", json={
            "title": "Security Test Case",
            "description": "Test case for error leakage.",
            "legal_domain": "Testing"
        })
        case_id = res.json()["id"]

        # Mock a service to throw an exception with a sensitive message
        with patch("app.services.missing_document_service.detect_missing_documents") as mock_service:
            secret_msg = "SUPER_SECRET_INTERNAL_DATABASE_CONNECTION_STRING"
            mock_service.side_effect = Exception(secret_msg)
            
            res = client.post(f"/api/cases/{case_id}/detect-missing-documents")
            
            check("Route returns 500 on unhandled exception", res.status_code == 500, f"Status: {res.status_code}")
            check("Sensitive error message is masked", secret_msg not in res.text, f"Response leaked info: {res.text}")

        print("\n--- Testing Path Traversal ---")
        # We also have an existing path traversal test in run_e2e_tests.py, let's verify it here as well.
        test_pdf_content = b"%PDF-1.4\n"
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("../../../etc/shadow", test_pdf_content, "application/pdf")}
        )
        # Even if it succeeds, it should just strip the path
        check("Path traversal upload handled gracefully", res.status_code in [201, 415])
        if res.status_code == 201:
            doc_data = res.json()
            check("Path traversal stripped from original filename", doc_data.get("original_filename") == "shadow")

    except Exception as e:
        print(f"Exception during tests: {e}")

    print("\n--- TEST SUMMARY ---")
    print(f"Passed: {len(tests_passed)}")
    print(f"Failed: {len(tests_failed)}")
    for f in tests_failed:
        print(f"  - {f}")

if __name__ == "__main__":
    run_tests()
