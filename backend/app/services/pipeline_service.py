import logging
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.document import Document
from app.models.evidence import EvidenceAnalysis
from app.schemas.pipeline import PipelineResponse, PipelineStepStatus
from app.services import (
    document_service,
    evidence_service,
    relevance_service,
    missing_document_service,
    similar_case_service,
    action_plan_service
)

logger = logging.getLogger(__name__)

def run_full_pipeline(case_id: int, db: Session) -> PipelineResponse:
    # 1. Verify case exists
    db_case = db.query(Case).filter(Case.id == case_id).first()
    if not db_case:
        raise ValueError(f"Case with ID {case_id} not found.")

    response = PipelineResponse(
        case_id=case_id,
        overall_status="failed",
        document_extraction=PipelineStepStatus(status="skipped"),
        evidence_analysis=PipelineStepStatus(status="skipped"),
        legal_relevance=PipelineStepStatus(status="skipped"),
        missing_documents=PipelineStepStatus(status="skipped"),
        similar_cases=PipelineStepStatus(status="skipped"),
        action_plan=PipelineStepStatus(status="skipped")
    )

    has_errors = False

    # 2. Document Extraction
    try:
        documents = db.query(Document).filter(Document.case_id == case_id).all()
        extracted_count = 0
        failed_extraction_count = 0
        
        for doc in documents:
            if doc.extraction_status not in ["completed", "no_text"]:
                result = document_service.extract_document_text(doc.id, db)
                if result and result.extraction_status == "completed":
                    extracted_count += 1
                elif result and result.extraction_status == "failed":
                    failed_extraction_count += 1
            elif doc.extraction_status == "completed":
                extracted_count += 1

        if documents:
            if failed_extraction_count > 0:
                has_errors = True
                response.document_extraction = PipelineStepStatus(
                    status="completed_with_errors", 
                    details=f"Failed to extract {failed_extraction_count} documents.",
                    records_processed=extracted_count
                )
            else:
                response.document_extraction = PipelineStepStatus(
                    status="completed", 
                    details="All documents extracted.",
                    records_processed=extracted_count
                )
        else:
            response.document_extraction = PipelineStepStatus(status="not_needed", details="No documents found.")
            
    except Exception as e:
        logger.error(f"Pipeline: Document extraction failed for case {case_id}: {e}")
        response.document_extraction = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # 3. Evidence Analysis
    try:
        evidence_count = 0
        failed_evidence_count = 0
        docs_with_text = [d for d in documents if d.extraction_status == "completed"]
        
        for doc in docs_with_text:
            existing_evidence = db.query(EvidenceAnalysis).filter(EvidenceAnalysis.document_id == doc.id).first()
            if not existing_evidence or existing_evidence.status != "completed":
                result = evidence_service.analyze_evidence(doc.id, db)
                if result and result.status == "completed":
                    evidence_count += 1
                else:
                    failed_evidence_count += 1
            else:
                evidence_count += 1

        if docs_with_text:
            if failed_evidence_count > 0:
                has_errors = True
                response.evidence_analysis = PipelineStepStatus(
                    status="completed_with_errors", 
                    details=f"Failed to analyze {failed_evidence_count} documents.",
                    records_processed=evidence_count
                )
            else:
                response.evidence_analysis = PipelineStepStatus(
                    status="completed", 
                    details="Evidence extracted from all documents.",
                    records_processed=evidence_count
                )
        else:
            response.evidence_analysis = PipelineStepStatus(status="not_needed", details="No text to analyze.")
            
    except Exception as e:
        logger.error(f"Pipeline: Evidence analysis failed for case {case_id}: {e}")
        response.evidence_analysis = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # 4. Legal Relevance
    try:
        # We run this even if no new documents were added, to force a refresh if facts changed
        relevance_results = relevance_service.analyze_legal_relevance(case_id, db)
        response.legal_relevance = PipelineStepStatus(
            status="completed", 
            records_processed=len(relevance_results)
        )
    except Exception as e:
        logger.error(f"Pipeline: Legal relevance failed for case {case_id}: {e}")
        response.legal_relevance = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # 5. Missing Documents
    try:
        missing_docs = missing_document_service.detect_missing_documents(case_id, db)
        response.missing_documents = PipelineStepStatus(
            status="completed", 
            records_processed=len(missing_docs)
        )
    except Exception as e:
        logger.error(f"Pipeline: Missing documents failed for case {case_id}: {e}")
        response.missing_documents = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # 6. Similar Cases
    try:
        similar_cases = similar_case_service.generate_similar_cases(case_id, db)
        response.similar_cases = PipelineStepStatus(
            status="completed", 
            records_processed=len(similar_cases)
        )
    except Exception as e:
        logger.error(f"Pipeline: Similar cases failed for case {case_id}: {e}")
        response.similar_cases = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # 7. Action Plan
    try:
        action_plan = action_plan_service.generate_action_plan(case_id, db)
        response.action_plan = PipelineStepStatus(
            status="completed", 
            records_processed=len(action_plan)
        )
    except Exception as e:
        logger.error(f"Pipeline: Action plan failed for case {case_id}: {e}")
        response.action_plan = PipelineStepStatus(status="failed", details="Internal error.")
        has_errors = True

    # Evaluate overall status
    if has_errors or any(s.status == "failed" for s in [
        response.legal_relevance, response.missing_documents, 
        response.similar_cases, response.action_plan
    ]):
        response.overall_status = "completed_with_errors"
    else:
        response.overall_status = "completed"

    # Edge case: everything failed
    if all(s.status == "failed" for s in [
        response.document_extraction, response.evidence_analysis, 
        response.legal_relevance, response.missing_documents, 
        response.similar_cases, response.action_plan
    ]):
        response.overall_status = "failed"

    return response
