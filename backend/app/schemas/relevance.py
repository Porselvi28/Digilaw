from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class LegalRelevanceResult(BaseModel):
    legal_source: str = Field(description="The legal source (e.g., Act name, Judgment title) retrieved.")
    act_judgment_info: str = Field(description="Specific section, rule, or citation information if available.")
    relevance_explanation: str = Field(description="Explanation of how the evidence fact relates to the legal source, using cautious language like 'may be relevant' or 'potentially relates to'.")
    relevance_score: int | None = Field(default=None, description="A score from 1 to 10 indicating the potential relevance, or None if not applicable.")

class LegalRelevanceAnalysisResponse(BaseModel):
    id: int
    case_id: int
    evidence_id: int
    fact_reference: str
    legal_source: str | None = None
    relevance_explanation: str | None = None
    relevance_score: int | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
