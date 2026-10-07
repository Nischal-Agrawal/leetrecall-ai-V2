import pandas as pd
import joblib


model = joblib.load(
    "ml/artifacts/xgboost_model.pkl"
)


difficulty_mapping = {
    "Easy": 0,
    "Medium": 1,
    "Hard": 2
}


def recommend_questions():

    sample_questions = [

        {
            "title": "Two Sum",
            "days_since_solved": 10,
            "difficulty": "Easy",
            "wrong_attempts": 0,
            "hints_used": 0,
            "confidence_score": 9,
            "revision_count": 2
        },

        {
            "title": "3Sum",
            "days_since_solved": 60,
            "difficulty": "Medium",
            "wrong_attempts": 3,
            "hints_used": 1,
            "confidence_score": 5,
            "revision_count": 0
        },

        {
            "title": "Word Ladder",
            "days_since_solved": 90,
            "difficulty": "Hard",
            "wrong_attempts": 5,
            "hints_used": 3,
            "confidence_score": 2,
            "revision_count": 0
        }

    ]

    recommendations = []

    for question in sample_questions:

        features = pd.DataFrame(
            [
                {
                    "days_since_solved":
                    question["days_since_solved"],

                    "difficulty":
                    difficulty_mapping[
                        question["difficulty"]
                    ],

                    "wrong_attempts":
                    question["wrong_attempts"],

                    "hints_used":
                    question["hints_used"],

                    "confidence_score":
                    question["confidence_score"],

                    "revision_count":
                    question["revision_count"]
                }
            ]
        )

        remember_probability = (
            model.predict_proba(features)[0][1]
        )

        forget_probability = (
            1 - remember_probability
        )

        recommendations.append(
            {
                "title":
                question["title"],

                "forget_probability":
                round(
                    forget_probability,
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


if __name__ == "__main__":

    results = recommend_questions()

    print("\nTOP QUESTIONS TO REVISE\n")

    for item in results:

        print(
            item["title"],
            "->",
            item["forget_probability"]
        )