from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_service import ask_legal_question


router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: AskRequest):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        return ask_legal_question(
            request.question
        )

    except Exception as error:
        import logging
        logging.getLogger(__name__).error("Ask endpoint error: %s", str(error))
        raise HTTPException(
            status_code=500,
            detail="An internal processing error occurred."
        )