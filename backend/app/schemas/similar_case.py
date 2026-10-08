from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class SimilarCaseResult(BaseModel):
    judgment_title: str = Field(description="The title or name of the similar judgment.")
    court: str | None = Field(default=None, description="The court that issued the judgment, if available.")
    judgment_year: str | None = Field(default=None, description="The year of the judgment, if available.")
    citation: str | None = Field(default=None, description="The legal citation or source identifier of the judgment, if available.")
    similarity_explanation: str = Field(description="Cautious explanation of how the factual or legal pattern is similar to the user's case.")
    relevant_passage: str | None = Field(default=None, description="A small snippet or summary of the most relevant part of the judgment.")

class SimilarCaseResponse(BaseModel):
    id: int
    case_id: int
    judgment_title: str
    court: str | None = None
    judgment_year: str | None = None
    citation: str | None = None
    similarity_score: float | None = None
    relevant_passage: str | None = None
    similarity_explanation: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
