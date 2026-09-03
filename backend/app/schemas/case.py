from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CaseBase(BaseModel):
    title: str
    description: str
    legal_domain: str

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
