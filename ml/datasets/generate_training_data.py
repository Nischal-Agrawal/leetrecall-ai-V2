import pandas as pd
import numpy as np

np.random.seed(42)

rows = []

for _ in range(5000):

    days_since_solved = np.random.randint(1, 120)

    difficulty = np.random.choice(
        ["Easy", "Medium", "Hard"]
    )

    wrong_attempts = np.random.randint(0, 6)

    hints_used = np.random.randint(0, 4)

    confidence_score = np.random.randint(1, 11)

    revision_count = np.random.randint(0, 6)

    retention_score = (
        confidence_score * 2
        + revision_count * 3
        - wrong_attempts * 2
        - hints_used
        - (days_since_solved / 10)
    )

    remembered = 1

    if retention_score < 5:
        remembered = 0

    rows.append(
        {
            "days_since_solved": days_since_solved,
            "difficulty": difficulty,
            "wrong_attempts": wrong_attempts,
            "hints_used": hints_used,
            "confidence_score": confidence_score,
            "revision_count": revision_count,
            "remembered": remembered
        }
    )

df = pd.DataFrame(rows)

df.to_csv(
    "ml/datasets/training_data.csv",
    index=False
)

print(
    f"Dataset generated with {len(df)} rows"
)