from backend.services.contest_analyzer_service import (
    analyze_contest
)

from backend.services.openai_coach import (
    generate_ai_advice
)


def generate_contest_review():

    contest_results = analyze_contest()

    if len(contest_results) == 0:

        return {
            "review":
            (
                "Excellent! None of the contest questions "
                "matched your current weak patterns."
            )
        }

    summary = []

    for question in contest_results:

        advice = generate_ai_advice(
            question=question["question"],
            forget_probability=0.85
        )

        summary.append(
            {
                "question": question["question"],
                "pattern": question["pattern"],
                "difficulty": question["difficulty"],
                "ai_review": advice
            }
        )

    return summary