from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class MissingDocumentRecommendationResult(BaseModel):
    document_category: str | None = Field(description="The general category of the document (e.g., 'Identity Proof', 'Medical Report', 'Police Report').")
    document_name: str = Field(description="The specific name or description of the document recommended.")
    requirement_level: str = Field(description="The requirement level. Must be one of: 'potentially required', 'recommended', 'optional'.")
    reason: str = Field(description="Concise reason explaining why this document may be relevant to the case.")
    related_evidence_fact: str | None = Field(default=None, description="The specific evidence fact that triggered this recommendation, if any.")
    related_legal_source: str | None = Field(default=None, description="The specific legal source or section that suggests this document might be needed, if any.")

class MissingDocumentRecommendationResponse(BaseModel):
    id: int
    case_id: int
    document_category: str | None = None
    document_name: str
    requirement_level: str
    reason: str
    related_evidence_fact: str | None = None
    related_legal_source: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
