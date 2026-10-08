import os
import fitz  # PyMuPDF
import docx
from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.ocr_service import extract_text_from_image_bytes, extract_text_from_image_file

MAX_OCR_PAGES = 20
MIN_TEXT_PER_PAGE = 50 # characters

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
    
    ocr_used = False
    page_count = 0
    
    try:
        if file_type == "txt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                extracted_text = f.read()
                
        elif file_type == "docx":
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_type in ["jpg", "jpeg", "png"]:
            extracted_text = extract_text_from_image_file(file_path)
            ocr_used = True
            page_count = 1
            
        elif file_type == "pdf":
            with fitz.open(file_path) as pdf_doc:
                page_count = len(pdf_doc)
                
                # Check for encrypted PDF
                if pdf_doc.needs_pass:
                    raise ValueError("Cannot extract text from a password-protected PDF.")

                for page_num, page in enumerate(pdf_doc):
                    page_text = page.get_text("text").strip()
                    
                    # If page has very little text, fallback to OCR
                    if len(page_text) < MIN_TEXT_PER_PAGE:
                        if page_num < MAX_OCR_PAGES:
                            # Convert page to image
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x resolution for better OCR
                            img_bytes = pix.tobytes("png")
                            ocr_text = extract_text_from_image_bytes(img_bytes)
                            page_text += f"\n[OCR EXTRACTED]: {ocr_text}"
                            ocr_used = True
                        else:
                            page_text += f"\n[OCR SKIPPED]: Page limit ({MAX_OCR_PAGES}) exceeded."
                            
                    extracted_text += page_text + "\n\n"
                    
        else:
            db_document.extraction_status = "failed"
            db_document.extraction_error = f"Unsupported file type for extraction: {file_type}"
            db.commit()
            return db_document
            
        # Check if text is completely empty or just whitespace
        cleaned_text = extracted_text.strip()
        
        db_document.ocr_used = ocr_used
        db_document.page_count = page_count
        db_document.extracted_character_count = len(cleaned_text)
        
        if len(cleaned_text) == 0:
            db_document.extraction_status = "no_text"
            db_document.ocr_status = "completed" if ocr_used else "not_needed"
            db_document.extraction_error = "Document contained no extractable text even after OCR."
        else:
            db_document.extraction_status = "completed"
            db_document.ocr_status = "completed" if ocr_used else "not_needed"
            db_document.extracted_text = extracted_text
            db_document.extraction_error = None
            
        db.commit()
        return db_document
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Document extraction error: %s", str(e))
        db_document.extraction_status = "failed"
        db_document.ocr_status = "failed" if ocr_used else "not_needed"
        db_document.extraction_error = "An internal processing error occurred during document extraction."
        db.commit()
        return db_document
