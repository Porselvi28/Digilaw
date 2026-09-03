from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter()

@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    try:
        db_case = Case(
            title=case.title,
            description=case.description,
            legal_domain=case.legal_domain
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
def get_cases(db: Session = Depends(get_db)):
    try:
        cases = db.query(Case).all()
        return cases
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving cases from the database."
        )

@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    try:
        db_case = db.query(Case).filter(Case.id == case_id).first()
        if db_case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found."
            )
        return db_case
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the case from the database."
        )
