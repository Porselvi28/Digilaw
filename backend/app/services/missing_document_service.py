import json
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.models.case import Case
from app.models.document import Document
from app.models.evidence import EvidenceAnalysis
from app.models.relevance import LegalRelevanceAnalysis
from app.models.missing_document import MissingDocumentRecommendation
from app.schemas.missing_document import MissingDocumentRecommendationResult
from app.services.rag_service import gemini_client

def detect_missing_documents(case_id: int, db: Session):
    # 1. Validate Case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    # 2. Retrieve existing documents
    documents = db.query(Document).filter(Document.case_id == case_id).all()
    
    # 3. Retrieve evidence facts
    evidence_analyses = db.query(EvidenceAnalysis).filter(
        EvidenceAnalysis.case_id == case_id,
        EvidenceAnalysis.status == "completed"
    ).all()
    
    # 4. Retrieve legal relevance
    relevance_analyses = db.query(LegalRelevanceAnalysis).filter(
        LegalRelevanceAnalysis.case_id == case_id,
        LegalRelevanceAnalysis.status == "completed"
    ).all()

    # Even if some components are missing, we can still recommend baseline documents based on legal domain,
    # but we should format the available context clearly.
    
    existing_docs_context = "\n".join([
        f"- {doc.original_filename} (Type: {doc.file_type})"
        for doc in documents
    ]) if documents else "None"

    evidence_context = []
    for ev in evidence_analyses:
        if ev.facts:
            claims = ev.facts.get("claims_allegations", [])
            events = ev.facts.get("events", [])
            for c in claims:
                evidence_context.append(f"- Claim/Allegation: {c}")
            for e in events:
                evidence_context.append(f"- Event: {e}")
    evidence_context_str = "\n".join(evidence_context) if evidence_context else "None"

    relevance_context = "\n".join([
        f"- Fact: {rel.fact_reference}\n  Source: {rel.legal_source}\n  Explanation: {rel.relevance_explanation}"
        for rel in relevance_analyses if rel.legal_source
    ]) if relevance_analyses else "None"

    prompt = f"""
You are DigiLaw, an expert Indian legal assistant.
Your task is to analyze the following case details and determine if there are any MISSING documents that the user should consider uploading to strengthen or proceed with their case.

CASE DETAILS:
Title: {case.title}
Domain: {case.legal_domain}
Description: {case.description}

ALREADY UPLOADED DOCUMENTS (Do not recommend these):
{existing_docs_context}

EXTRACTED EVIDENCE FACTS:
{evidence_context_str}

LEGAL RELEVANCE FINDINGS:
{relevance_context}

INSTRUCTIONS:
1. Identify documents that are missing but would be useful or potentially required for this case.
2. Categorize the requirement level as exactly one of: "potentially required", "recommended", or "optional".
3. NEVER claim a document is legally mandatory unless it is directly supported by the LEGAL RELEVANCE FINDINGS. Use "potentially required" if it's a standard requirement.
4. For each recommendation, provide a concise reason explaining why it may be relevant.
5. If applicable, connect it to an extracted evidence fact or a legal source provided above.
6. Compare your recommendations against the ALREADY UPLOADED DOCUMENTS to avoid suggesting documents they already have.
7. Return the results as a JSON array of objects.

Output ONLY valid JSON matching this schema for each object:
{{
  "document_category": "string or null",
  "document_name": "string",
  "requirement_level": "string",
  "reason": "string",
  "related_evidence_fact": "string or null",
  "related_legal_source": "string or null"
}}
"""

    models_to_try = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    last_error = None
    response_text = ""

    for model_name in models_to_try:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            response_text = response.text
            break
        except Exception as e:
            print(f"Gemini model failed for missing documents: {model_name}")
            print(str(e))
            last_error = e

    if not response_text and last_error:
        # Create a failed record
        fail_record = MissingDocumentRecommendation(
            case_id=case_id,
            document_name="Error",
            requirement_level="optional",
            reason="Failed to generate recommendations.",
            status="failed",
            error_message="An internal processing error occurred during generation."
        )
        db.add(fail_record)
        db.commit()
        raise RuntimeError("All Gemini models failed for missing document detection.")

    # Clean JSON
    json_str = response_text.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()

    try:
        parsed_data = json.loads(json_str)
        if not isinstance(parsed_data, list):
            parsed_data = [parsed_data]
            
        adapter = TypeAdapter(list[MissingDocumentRecommendationResult])
        validated_results = adapter.validate_python(parsed_data)
        
        # Clear existing pending/failed/completed recommendations for this case to avoid duplicates if re-run
        db.query(MissingDocumentRecommendation).filter(
            MissingDocumentRecommendation.case_id == case_id
        ).delete()
        
        saved_records = []
        for res in validated_results:
            record = MissingDocumentRecommendation(
                case_id=case_id,
                document_category=res.document_category,
                document_name=res.document_name,
                requirement_level=res.requirement_level,
                reason=res.reason,
                related_evidence_fact=res.related_evidence_fact,
                related_legal_source=res.related_legal_source,
                status="completed"
            )
            db.add(record)
            saved_records.append(record)
            
        db.commit()
        for r in saved_records:
            db.refresh(r)
            
        return saved_records

    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Missing doc parse error: %s", str(e))
        db.rollback()
        fail_record = MissingDocumentRecommendation(
            case_id=case_id,
            document_name="Error",
            requirement_level="optional",
            reason="Failed to parse JSON.",
            status="failed",
            error_message="An internal processing error occurred while parsing the output."
        )
        db.add(fail_record)
        db.commit()
        raise ValueError("Failed to parse Gemini output due to an internal error.")

def get_missing_documents(case_id: int, db: Session):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")
        
    return db.query(MissingDocumentRecommendation).filter(
        MissingDocumentRecommendation.case_id == case_id
    ).all()
