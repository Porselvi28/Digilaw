import json
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.evidence import EvidenceAnalysis
from app.schemas.evidence import FactExtractionResult
from app.services.rag_service import gemini_client
import pydantic

def analyze_evidence(document_id: int, db: Session) -> EvidenceAnalysis:
    """
    Analyzes an uploaded document for factual evidence using Gemini.
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        return None
        
    # Check if text extraction was successful
    if not db_document.extracted_text or db_document.extraction_status != "completed":
        raise ValueError("Document text has not been extracted or is empty.")
        
    text_content = db_document.extracted_text
    
    # Look for existing analysis
    existing_evidence = db.query(EvidenceAnalysis).filter(EvidenceAnalysis.document_id == document_id).first()
    if existing_evidence:
        evidence = existing_evidence
        evidence.status = "pending"
        evidence.error_message = None
        evidence.facts = None
    else:
        # Create a new evidence record
        evidence = EvidenceAnalysis(
            document_id=document_id,
            case_id=db_document.case_id,
            status="pending"
        )
        db.add(evidence)
        
    db.commit()
    db.refresh(evidence)
    
    # Prompt for Gemini
    prompt = f"""
You are an expert legal assistant. Analyze the following document and extract key factual evidence.
DO NOT make legal conclusions. Use phrasing like "the document states" or "the document contains" instead of claiming something is "proven".

Extract the following information:
- People and their roles
- Organizations
- Important dates
- Locations
- Key events described
- Monetary amounts mentioned
- Claims or allegations made
- Important factual statements
- Document type and purpose

Return the result as STRICT, VALID JSON that matches this exact schema (no markdown, just raw JSON):
{{
  "people_roles": ["list of strings"],
  "organizations": ["list of strings"],
  "dates": ["list of strings"],
  "locations": ["list of strings"],
  "events": ["list of strings"],
  "monetary_amounts": ["list of strings"],
  "claims_allegations": ["list of strings"],
  "important_statements": ["list of strings"],
  "document_type_purpose": "string"
}}

Here is the document text:
---------------------
{text_content}
---------------------
"""

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    last_error = None
    response_text = None

    for model_name in models_to_try:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            response_text = response.text
            break
        except Exception as e:
            print(f"Gemini model failed: {model_name} - {str(e)}")
            last_error = e

    if not response_text:
        evidence.status = "failed"
        evidence.error_message = "All Gemini models failed due to an internal processing error."
        db.commit()
        db.refresh(evidence)
        return evidence
        
    try:
        # Clean response if it contains markdown code blocks
        raw_json = response_text.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:]
        if raw_json.startswith("```"):
            raw_json = raw_json[3:]
        if raw_json.endswith("```"):
            raw_json = raw_json[:-3]
        raw_json = raw_json.strip()
            
        # Parse and validate with Pydantic
        parsed_data = json.loads(raw_json)
        validated_data = FactExtractionResult(**parsed_data)
        
        evidence.facts = validated_data.model_dump()
        evidence.status = "completed"
        
    except pydantic.ValidationError as e:
        evidence.status = "failed"
        evidence.error_message = f"AI returned invalid format: {str(e)}"
    except json.JSONDecodeError as e:
        evidence.status = "failed"
        evidence.error_message = f"AI returned malformed JSON: {str(e)}"
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("AI processing failed: %s", str(e))
        evidence.status = "failed"
        evidence.error_message = "AI processing failed due to an internal error."
        
    db.commit()
    db.refresh(evidence)
    
    return evidence
