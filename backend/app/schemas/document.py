from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    case_id: int
    original_filename: str
    file_type: str
    file_size: int
    status: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentExtractionResponse(BaseModel):
    id: int
    case_id: int
    original_filename: str
    extraction_status: str
    extracted_text_length: int
    extracted_text: str | None = None

    model_config = ConfigDict(from_attributes=True)
