import joblib
import pandas as pd


model = joblib.load(
    "ml/artifacts/xgboost_model.pkl"
)


difficulty_mapping = {
    "Easy": 0,
    "Medium": 1,
    "Hard": 2
}


def predict_retention(
    days_since_solved,
    difficulty,
    wrong_attempts,
    hints_used,
    confidence_score,
    revision_count
):

    difficulty = (
        difficulty_mapping[difficulty]
    )

    data = pd.DataFrame(
        [
            {
                "days_since_solved": days_since_solved,
                "difficulty": difficulty,
                "wrong_attempts": wrong_attempts,
                "hints_used": hints_used,
                "confidence_score": confidence_score,
                "revision_count": revision_count
            }
        ]
    )

    prediction = model.predict(data)[0]

    probability = (
        model.predict_proba(data)[0][1]
    )

    return {
        "remembered": int(prediction),
        "probability": round(
            float(probability),
            4
        )
    }


if __name__ == "__main__":

    result = predict_retention(
        days_since_solved=40,
        difficulty="Medium",
        wrong_attempts=3,
        hints_used=1,
        confidence_score=5,
        revision_count=0
    )

    print(result)