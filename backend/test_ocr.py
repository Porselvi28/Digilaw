import os
import pytest
import sys
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import fitz

from app.main import app
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def override_get_current_active_user():
    return User(id=1, email="legacy_admin@digilaw.ai", is_active=True)

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

from app.database.connection import get_db
from app.database.base import Base
from app.models.document import Document
from app.services.document_service import extract_document_text

# Setup In-Memory SQLite for Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# Helper to create a dummy document in DB
def create_dummy_doc(db, case_id, filename, file_type, file_path):
    doc = Document(
        case_id=case_id,
        original_filename=filename,
        stored_filename=filename,
        file_type=file_type,
        file_size=1024,
        file_path=file_path,
        status="uploaded",
        extraction_status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@patch("app.services.document_service.extract_text_from_image_file")
def test_ocr_jpg_document(mock_extract_file):
    # Setup
    mock_extract_file.return_value = "Mocked JPG OCR Text"
    db = TestingSessionLocal()
    
    case_response = client.post("/api/cases", json={"title": "OCR Case", "description": "test", "legal_domain": "test"})
    case_id = case_response.json()["id"]
    
    # Create a fake JPG file
    os.makedirs("uploads", exist_ok=True)
    fake_jpg = "uploads/test.jpg"
    with open(fake_jpg, "wb") as f:
        f.write(b"fake image data")
        
    doc = create_dummy_doc(db, case_id, "test.jpg", "jpg", fake_jpg)
    
    # Run extraction
    updated_doc = extract_document_text(doc.id, db)
    
    # Verify
    assert updated_doc.extraction_status == "completed"
    assert updated_doc.ocr_used is True
    assert updated_doc.ocr_status == "completed"
    assert updated_doc.page_count == 1
    assert "Mocked JPG OCR Text" in updated_doc.extracted_text
    
    # Cleanup
    os.remove(fake_jpg)

@patch("app.services.document_service.extract_text_from_image_bytes")
def test_ocr_scanned_pdf_fallback(mock_extract_bytes):
    # Setup
    mock_extract_bytes.return_value = "Mocked PDF OCR Text"
    db = TestingSessionLocal()
    
    # Create an empty PDF (scanned equivalent, no text)
    os.makedirs("uploads", exist_ok=True)
    fake_pdf = "uploads/scanned.pdf"
    
    doc = fitz.open()
    page = doc.new_page() # Empty page with no text
    doc.save(fake_pdf)
    doc.close()
    
    db_doc = create_dummy_doc(db, 1, "scanned.pdf", "pdf", fake_pdf)
    
    # Run extraction
    updated_doc = extract_document_text(db_doc.id, db)
    
    # Verify
    assert updated_doc.extraction_status == "completed"
    assert updated_doc.ocr_used is True
    assert updated_doc.ocr_status == "completed"
    assert updated_doc.page_count == 1
    assert "[OCR EXTRACTED]: Mocked PDF OCR Text" in updated_doc.extracted_text
    
    # Cleanup
    os.remove(fake_pdf)

def test_ocr_normal_pdf_no_fallback():
    # Setup
    db = TestingSessionLocal()
    os.makedirs("uploads", exist_ok=True)
    fake_pdf = "uploads/normal.pdf"
    
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a normal text PDF with plenty of text over 50 characters so it won't OCR.")
    doc.save(fake_pdf)
    doc.close()
    
    db_doc = create_dummy_doc(db, 1, "normal.pdf", "pdf", fake_pdf)
    
    # Run extraction
    updated_doc = extract_document_text(db_doc.id, db)
    
    # Verify
    assert updated_doc.extraction_status == "completed"
    assert updated_doc.ocr_used is False
    assert updated_doc.ocr_status == "not_needed"
    assert "This is a normal text PDF" in updated_doc.extracted_text
    
    # Cleanup
    os.remove(fake_pdf)
