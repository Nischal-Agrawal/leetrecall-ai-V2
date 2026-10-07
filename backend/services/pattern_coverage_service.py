from collections import defaultdict

from backend.database.connection import SessionLocal

from backend.models.question import Question
from backend.models.solve import Solve


def calculate_pattern_coverage():

    db = SessionLocal()

    questions = db.query(
        Question
    ).all()

    solves = db.query(
        Solve
    ).all()

    pattern_total = defaultdict(int)

    pattern_solved = defaultdict(int)

    question_pattern = {}

    for question in questions:

        pattern = question.pattern

        pattern_total[
            pattern
        ] += 1

        question_pattern[
            question.id
        ] = pattern

    for solve in solves:

        pattern = question_pattern.get(
            solve.question_id
        )

        if pattern:

            pattern_solved[
                pattern
            ] += 1

    results = []

    for pattern in pattern_total:

        coverage = (
            pattern_solved[pattern]
            /
            pattern_total[pattern]
        ) * 100

        results.append(
            {
                "pattern": pattern,
                "coverage": round(
                    coverage,
                    2
                )
            }
        )

    db.close()

    return results