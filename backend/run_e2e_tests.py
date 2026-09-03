import sys
import os
from pathlib import Path
from sqlalchemy import text
from app.database.connection import engine
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("Initializing TestClient (this will load models and DB)...")
    client = TestClient(app)
    print("TestClient initialized successfully.")

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
        # Create a new case to associate documents with
        print("Creating a case for document tests...")
        case_payload = {
            "title": "Document Test Case",
            "description": "Test case for document upload.",
            "legal_domain": "Testing"
        }
        res = client.post("/api/cases", json=case_payload)
        check("Case created", res.status_code == 201)
        case_id = res.json()["id"]

        # Prepare a dummy PDF file
        test_pdf_content = b"%PDF-1.4\n%..."
        
        print("Running POST /api/documents/upload...")
        # Valid upload
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("test_doc.pdf", test_pdf_content, "application/pdf")}
        )
        check("Valid upload succeeds", res.status_code == 201, f"Status code {res.status_code} - {res.text}")
        doc_data = res.json()
        check("Returned document has id, original_filename, file_type, size", all(k in doc_data for k in ["id", "original_filename", "file_type", "file_size"]))
        check("Original filename preserved", doc_data.get("original_filename") == "test_doc.pdf")
        doc_id = doc_data.get("id")

        # Invalid case ID
        print("Testing upload with invalid case ID...")
        res = client.post(
            "/api/documents/upload",
            data={"case_id": "999999"},
            files={"file": ("test_doc.pdf", test_pdf_content, "application/pdf")}
        )
        check("Invalid case ID returns 404", res.status_code == 404)

        # Invalid extension
        print("Testing unsupported file type...")
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("malicious.exe", b"MZ...", "application/x-msdownload")}
        )
        check("Unsupported file type rejected", res.status_code == 415)

        # Empty file
        print("Testing empty file...")
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        check("Empty file rejected", res.status_code == 400)

        # Path traversal test
        print("Testing path traversal attempt in filename...")
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("../../../etc/passwd.pdf", test_pdf_content, "application/pdf")}
        )
        check("Path traversal attempt uploaded safely", res.status_code == 201)
        safe_doc_data = res.json()
        safe_doc_id = safe_doc_data.get("id")

        # Verify DB and File system directly
        print("Checking PostgreSQL directly for Document...")
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM documents WHERE id = {doc_id}"))
            db_doc = result.fetchone()
            check("Document DB record exists", db_doc is not None)
            
            if db_doc:
                # Get column indices dynamically
                keys = list(result.keys())
                path_idx = keys.index("file_path")
                file_path = db_doc[path_idx]
                
                check("Physical file exists on disk", os.path.exists(file_path))
                check("File is in uploads directory", "uploads" in file_path)
                
            # Verify safe filename
            result = conn.execute(text(f"SELECT * FROM documents WHERE id = {safe_doc_id}"))
            safe_db_doc = result.fetchone()
            check("Path traversal DB record exists safely", safe_db_doc is not None)
            if safe_db_doc:
                orig_name_idx = list(result.keys()).index("original_filename")
                check("Path traversal stripped from original filename", safe_db_doc[orig_name_idx] == "passwd.pdf")

        # Test Text Extraction
        print("Testing text extraction for TXT file...")
        res = client.post(
            "/api/documents/upload",
            data={"case_id": str(case_id)},
            files={"file": ("test_doc.txt", b"Hello DigiLaw! This is a test document.", "text/plain")}
        )
        check("TXT upload succeeds", res.status_code == 201)
        txt_doc_id = res.json()["id"]

        res = client.post(f"/api/documents/{txt_doc_id}/extract")
        check("TXT extraction API succeeds", res.status_code == 200)
        ext_data = res.json()
        check("Extraction status is completed", ext_data["extraction_status"] == "completed")
        check("Extracted text matches", ext_data["extracted_text"] == "Hello DigiLaw! This is a test document.")
        check("Extracted text length is correct", ext_data["extracted_text_length"] > 0)

        # PDF Extraction Test (using the previously uploaded test_doc.pdf)
        print("Testing text extraction for PDF file...")
        # Note: test_pdf_content was b"%PDF-1.4\n%..." which is an invalid PDF and PyMuPDF will fail to extract text from it.
        # Let's see how it behaves:
        res = client.post(f"/api/documents/{doc_id}/extract")
        check("PDF extraction API succeeds (handles corrupt gracefully)", res.status_code == 200)
        pdf_ext_data = res.json()
        check("PDF extraction status is failed due to invalid PDF", pdf_ext_data["extraction_status"] == "failed")
        
        # Invalid document ID
        print("Testing extraction for invalid document ID...")
        res = client.post("/api/documents/999999/extract")
        check("Invalid document ID returns 404", res.status_code == 404)


    except Exception as e:
        print(f"Exception during tests: {e}")

    print("\n--- TEST SUMMARY ---")
    print(f"Passed: {len(tests_passed)}")
    print(f"Failed: {len(tests_failed)}")
    for f in tests_failed:
        print(f"  - {f}")

if __name__ == "__main__":
    run_tests()
