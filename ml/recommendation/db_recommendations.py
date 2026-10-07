import pandas as pd
import joblib

from sqlalchemy import func

from backend.database.connection import SessionLocal

from backend.models.question import Question
from backend.models.solve import Solve
from backend.models.revision import Revision


model = joblib.load(
    "ml/artifacts/xgboost_model.pkl"
)


difficulty_mapping = {
    "Easy": 0,
    "Medium": 1,
    "Hard": 2
}


def generate_recommendations():

    db = SessionLocal()

    try:

        recommendations = []

        # -----------------------------
        # Load all required data ONCE
        # -----------------------------

        questions = db.query(Question).all()

        question_map = {
            q.id: q
            for q in questions
        }

        revision_counts = dict(

            db.query(
                Revision.question_id,
                func.count(Revision.id)
            )
            .group_by(
                Revision.question_id
            )
            .all()

        )

        solves = db.query(Solve).all()

        # -----------------------------
        # Generate predictions
        # -----------------------------

        for solve in solves:

            question = question_map.get(
                solve.question_id
            )

            if question is None:
                continue

            revision_count = revision_counts.get(
                solve.question_id,
                0
            )

            features = pd.DataFrame([
                {
                    "days_since_solved": 30,

                    "difficulty":
                    difficulty_mapping[
                        question.difficulty
                    ],

                    "wrong_attempts":
                    solve.wrong_attempts,

                    "hints_used":
                    solve.hints_used,

                    "confidence_score":
                    solve.confidence_score,

                    "revision_count":
                    revision_count
                }
            ])

            remember_probability = (
                model.predict_proba(
                    features
                )[0][1]
            )

            forget_probability = (
                1 - remember_probability
            )

            recommendations.append(
                {
                    "question_id":
                    question.id,

                    "title":
                    question.title,

                    "forget_probability":
                    round(
                        float(
                            forget_probability
                        ),
                        4
                    )
                }
            )

        recommendations.sort(
            key=lambda x:
            x["forget_probability"],
            reverse=True
        )

        return recommendations

    finally:

        db.close()


if __name__ == "__main__":

    results = generate_recommendations()

    print("\nDATABASE RECOMMENDATIONS\n")

    for r in results:

        print(
            r["title"],
            "->",
            r["forget_probability"]
        )