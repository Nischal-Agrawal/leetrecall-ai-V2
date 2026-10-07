import pandas as pd

from backend.services.weak_pattern_service import (
    get_weak_patterns
)


def analyze_contest():

    contest_df = pd.read_csv(
        "datasets/contest/sample_contest.csv"
    )

    weak_patterns = get_weak_patterns()

    weak_pattern_names = [
        item["pattern"]
        for item in weak_patterns
    ]

    recommendations = []

    for _, row in contest_df.iterrows():

        if row["pattern"] in weak_pattern_names:

            recommendations.append(
                {
                    "question": row["question"],
                    "pattern": row["pattern"],
                    "difficulty": row["difficulty"],
                    "reason": (
                        "This contest question belongs to one "
                        "of your weakest DSA patterns."
                    )
                }
            )

    return recommendations