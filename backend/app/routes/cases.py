from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse
from app.schemas.relevance import LegalRelevanceAnalysisResponse
from app.schemas.missing_document import MissingDocumentRecommendationResponse
from app.schemas.similar_case import SimilarCaseResponse
from app.schemas.action_plan import ActionPlanResponse
from app.schemas.pipeline import PipelineResponse
from app.services import relevance_service, missing_document_service, similar_case_service, action_plan_service, pipeline_service
from app.dependencies.auth import get_current_active_user

router = APIRouter()

def get_user_case(case_id: int, current_user: User, db: Session) -> Case:
    db_case = db.query(Case).filter(Case.id == case_id, Case.user_id == current_user.id).first()
    if db_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found."
        )
    return db_case

@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case: CaseCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        db_case = Case(
            title=case.title,
            description=case.description,
            legal_domain=case.legal_domain,
            user_id=current_user.id
        )
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        return db_case
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the case to the database."
        )

@router.get("/cases", response_model=list[CaseResponse])
def get_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        cases = db.query(Case).filter(Case.user_id == current_user.id).all()
        return cases
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving cases from the database."
        )

@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        db_case = get_user_case(case_id, current_user, db)
        return db_case
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the case from the database."
        )

@router.post("/cases/{case_id}/analyze-legal-relevance", response_model=list[LegalRelevanceAnalysisResponse])
def analyze_legal_relevance(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = relevance_service.analyze_legal_relevance(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.post("/cases/{case_id}/detect-missing-documents", response_model=list[MissingDocumentRecommendationResponse])
def detect_missing_documents(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = missing_document_service.detect_missing_documents(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.get("/cases/{case_id}/missing-documents", response_model=list[MissingDocumentRecommendationResponse])
def get_missing_documents(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = missing_document_service.get_missing_documents(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.post("/cases/{case_id}/similar-cases", response_model=list[SimilarCaseResponse])
def create_similar_cases(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = similar_case_service.generate_similar_cases(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.get("/cases/{case_id}/similar-cases", response_model=list[SimilarCaseResponse])
def read_similar_cases(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = similar_case_service.get_similar_cases(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.post("/cases/{case_id}/generate-action-plan", response_model=list[ActionPlanResponse])
def generate_action_plan(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = action_plan_service.generate_action_plan(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.get("/cases/{case_id}/action-plan", response_model=list[ActionPlanResponse])
def get_action_plan(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = action_plan_service.get_action_plan(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.post("/cases/{case_id}/run-pipeline", response_model=PipelineResponse)
def run_pipeline(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    get_user_case(case_id, current_user, db)
    try:
        results = pipeline_service.run_full_pipeline(case_id, db)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Cases pipeline endpoint error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while running the pipeline."
        )

