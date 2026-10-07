from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.models.solve import Solve

from backend.schemas.solve_schema import (
    SolveCreate,
    SolveResponse
)

router = APIRouter(
    prefix="/solves",
    tags=["Solves"]
)


@router.post(
    "/",
    response_model=SolveResponse
)
def create_solve(
    solve: SolveCreate,
    db: Session = Depends(get_db)
):
    db_solve = Solve(
        user_id=solve.user_id,
        question_id=solve.question_id,
        time_taken_minutes=solve.time_taken_minutes,
        wrong_attempts=solve.wrong_attempts,
        hints_used=solve.hints_used,
        confidence_score=solve.confidence_score
    )

    db.add(db_solve)

    db.commit()

    db.refresh(db_solve)

    return db_solve


@router.get(
    "/"
)
def get_solves(
    db: Session = Depends(get_db)
):
    return db.query(Solve).all()