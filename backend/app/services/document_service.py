import os
import fitz  # PyMuPDF
import docx
from sqlalchemy.orm import Session
from app.models.document import Document

def extract_document_text(document_id: int, db: Session) -> Document:
    # Fetch the document
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        return None
        
    file_path = db_document.file_path
    
    if not os.path.exists(file_path):
        db_document.extraction_status = "failed"
        db_document.extraction_error = "Physical file not found on disk."
        db.commit()
        return db_document

    extracted_text = ""
    file_type = db_document.file_type.lower()
    
    try:
        if file_type == "txt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                extracted_text = f.read()
                
        elif file_type == "docx":
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_type == "pdf":
            with fitz.open(file_path) as pdf_doc:
                for page in pdf_doc:
                    extracted_text += page.get_text("text") + "\n\n"
                    
        else:
            db_document.extraction_status = "failed"
            db_document.extraction_error = f"Unsupported file type for extraction: {file_type}"
            db.commit()
            return db_document
            
        # Check if text is completely empty or just whitespace (e.g. scanned PDF)
        if len(extracted_text.strip()) == 0:
            db_document.extraction_status = "no_text"
            db_document.extraction_error = "Document appears to be a scanned image with no machine-readable text. OCR is required."
        else:
            db_document.extraction_status = "completed"
            db_document.extracted_text = extracted_text
            db_document.extraction_error = None
            
        db.commit()
        return db_document
        
    except Exception as e:
        db_document.extraction_status = "failed"
        db_document.extraction_error = f"Extraction error: {str(e)}"
        db.commit()
        return db_document
