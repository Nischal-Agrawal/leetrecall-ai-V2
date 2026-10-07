from fastapi import APIRouter
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal

from backend.models.recommendation import Recommendation
from backend.models.question import Question

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/")
def get_recommendations():

    db: Session = SessionLocal()

    try:

        rows = (
            db.query(
                Recommendation.question_id,
                Recommendation.forget_probability,
                Question.title,
                Question.topic,
                Question.pattern,
                Question.difficulty,
                Question.url,
            )
            .join(
                Question,
                Recommendation.question_id == Question.id,
            )
            .order_by(
                Recommendation.forget_probability.desc()
            )
            .limit(100)
            .all()
        )

        return [
            {
                "question_id": row.question_id,
                "title": row.title,
                "topic": row.topic,
                "pattern": row.pattern,
                "difficulty": row.difficulty,
                "url": row.url,
                "forget_probability": row.forget_probability,
            }
            for row in rows
        ]

    finally:
        db.close()