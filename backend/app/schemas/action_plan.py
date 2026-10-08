from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ActionPlanStepResult(BaseModel):
    action_title: str = Field(description="A concise title for the action step.")
    description: str = Field(description="A detailed explanation of the action to be taken.")
    priority: str = Field(description="The priority of this action (e.g., 'Immediate', 'High', 'Medium', 'Low').")
    sequence_order: int = Field(description="The chronological order of this step (1, 2, 3...).")
    action_category: str = Field(description="Category of the action (e.g., 'Document Collection', 'Procedural Step', 'Escalation').")
    required_documents: str | None = Field(default=None, description="Any specific documents or evidence required for this step.")
    related_legal_source: str | None = Field(default=None, description="Relevant legal section or rule grounding this step, if available.")
    rationale: str = Field(description="Why this step is recommended based on the available facts or law.")

class ActionPlanResponse(BaseModel):
    id: int
    case_id: int
    action_title: str
    description: str
    priority: str
    sequence_order: int
    action_category: str
    required_documents: str | None = None
    related_legal_source: str | None = None
    rationale: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
