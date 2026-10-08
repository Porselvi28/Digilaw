from pydantic import BaseModel
from typing import Dict, Any, Optional

class PipelineStepStatus(BaseModel):
    status: str  # "completed", "failed", "skipped", "not_needed"
    details: Optional[str] = None
    records_processed: Optional[int] = 0

class PipelineResponse(BaseModel):
    case_id: int
    overall_status: str # "completed", "completed_with_errors", "failed"
    document_extraction: PipelineStepStatus
    evidence_analysis: PipelineStepStatus
    legal_relevance: PipelineStepStatus
    missing_documents: PipelineStepStatus
    similar_cases: PipelineStepStatus
    action_plan: PipelineStepStatus
