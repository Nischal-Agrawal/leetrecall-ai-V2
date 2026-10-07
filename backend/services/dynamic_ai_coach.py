from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal

from backend.models.recommendation import Recommendation
from backend.models.question import Question

from backend.services.openai_coach import generate_ai_advice


def get_dynamic_advice():

    db: Session = SessionLocal()

    try:

        rows = (
            db.query(
                Recommendation.forget_probability,
                Question.title,
            )
            .join(
                Question,
                Recommendation.question_id == Question.id,
            )
            .order_by(
                Recommendation.forget_probability.desc()
            )
            .limit(5)
            .all()
        )

        results = []

        for row in rows:

            advice = generate_ai_advice(
                question=row.title,
                forget_probability=row.forget_probability,
            )

            results.append(
                {
                    "question": row.title,
                    "forget_probability": row.forget_probability,
                    "advice": advice,
                }
            )

        return results

    finally:

        db.close()