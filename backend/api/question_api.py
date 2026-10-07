from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.question import Question

from backend.schemas.question_schema import (
    QuestionCreate,
    QuestionResponse
)

router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@router.post(
    "/",
    response_model=QuestionResponse
)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db)
):
    db_question = Question(
        title=question.title,
        platform=question.platform,
        topic=question.topic,
        pattern=question.pattern,
        difficulty=question.difficulty,
        tags=question.tags,
        url=question.url
    )

    db.add(db_question)

    db.commit()

    db.refresh(db_question)

    return db_question


@router.get(
    "/",
    response_model=list[QuestionResponse]
)
def get_questions(
    db: Session = Depends(get_db)
):
    return db.query(Question).all()