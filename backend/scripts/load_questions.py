import pandas as pd

from backend.database.connection import SessionLocal

from backend.models.question import Question


def load_questions():

    db = SessionLocal()

    try:

        df = pd.read_csv(
            "datasets/raw/questions.csv"
        )

        inserted = 0

        for _, row in df.iterrows():

            exists = (
                db.query(Question)
                .filter(
                    Question.title == row["title"]
                )
                .first()
            )

            if exists:
                continue

            question = Question(
                title=row["title"],
                platform=row["platform"],
                topic=row["topic"],
                pattern=row["pattern"],
                difficulty=row["difficulty"],
                tags=row["tags"],
                url=row["url"]
            )

            db.add(question)

            inserted += 1

        db.commit()

        print(
            f"{inserted} questions inserted"
        )

    finally:

        db.close()


if __name__ == "__main__":

    load_questions()