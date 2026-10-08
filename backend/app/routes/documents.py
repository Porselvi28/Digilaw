import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.models.case import Case
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentExtractionResponse
from app.schemas.evidence import EvidenceAnalysisResponse
from app.services import document_service
from app.services import evidence_service
from app.dependencies.auth import get_current_active_user

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/jpeg",
    "image/png"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

def get_user_document(document_id: int, current_user: User, db: Session) -> Document:
    # Join with Case to verify ownership
    db_document = db.query(Document).join(Case).filter(
        Document.id == document_id, 
        Case.user_id == current_user.id
    ).first()
    
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )
    return db_document

@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    case_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Validate Case Exists and belongs to user
    db_case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found."
        )

    # 2. Validate empty file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided."
        )

    # 3. Validate File Extension & MIME Type
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type {ext} is not supported."
        )
    
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"MIME type {file.content_type} is not supported."
        )

    # 4. Read File Content & Size validation
    try:
        file_content = file.file.read()
        file_size = len(file_content)
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty."
            )
            
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE} bytes."
            )
    finally:
        # Reset file pointer for potential subsequent reading/saving (though we can write directly from memory now)
        file.file.seek(0)

    # 5. Safe Filename Generation
    safe_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_filename

    # 6. Write to Disk FIRST
    file_written = False
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        file_written = True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving the file to disk."
        )

    # 7. Create Database Record AFTER file is stored
    db_document = Document(
        case_id=case_id,
        original_filename=Path(file.filename).name, # Strip traversal attempts
        stored_filename=safe_filename,
        file_type=ext.lstrip("."),
        file_size=file_size,
        file_path=str(file_path.absolute()),
        status="uploaded"
    )

    try:
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
    except SQLAlchemyError as e:
        db.rollback()
        # If DB fails, remove the stored file so no orphan file remains
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass # Already failing, ignore cleanup error
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while associating the document."
        )
    
    return db_document

@router.post("/documents/{document_id}/extract", response_model=DocumentExtractionResponse)
def extract_document(
    document_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify the document exists and belongs to user
    get_user_document(document_id, current_user, db)

    # Perform text extraction
    updated_document = document_service.extract_document_text(document_id, db)
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} could not be retrieved during extraction."
        )
        
    extracted_text_length = len(updated_document.extracted_text) if updated_document.extracted_text else 0
        
    return DocumentExtractionResponse(
        id=updated_document.id,
        case_id=updated_document.case_id,
        original_filename=updated_document.original_filename,
        extraction_status=updated_document.extraction_status,
        extracted_text_length=extracted_text_length,
        extracted_text=updated_document.extracted_text
    )

@router.post("/documents/{document_id}/analyze-evidence", response_model=EvidenceAnalysisResponse)
def analyze_evidence_for_document(
    document_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_document(document_id, current_user, db)

    try:
        evidence = evidence_service.analyze_evidence(document_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Evidence analysis endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing evidence."
        )
        
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )
        
    return evidence
