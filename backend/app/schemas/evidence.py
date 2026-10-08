from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class FactExtractionResult(BaseModel):
    people_roles: list[str] = Field(default_factory=list, description="People and their roles mentioned in the document.")
    organizations: list[str] = Field(default_factory=list, description="Organizations mentioned.")
    dates: list[str] = Field(default_factory=list, description="Important dates mentioned.")
    locations: list[str] = Field(default_factory=list, description="Locations mentioned.")
    events: list[str] = Field(default_factory=list, description="Key events described.")
    monetary_amounts: list[str] = Field(default_factory=list, description="Monetary amounts mentioned.")
    claims_allegations: list[str] = Field(default_factory=list, description="Claims or allegations made.")
    important_statements: list[str] = Field(default_factory=list, description="Other important factual statements.")
    document_type_purpose: str = Field(default="", description="The type and purpose of the document.")

class EvidenceAnalysisResponse(BaseModel):
    id: int
    document_id: int
    case_id: int
    status: str
    facts: dict | list | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
