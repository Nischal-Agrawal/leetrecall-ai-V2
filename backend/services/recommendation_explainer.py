from ml.recommendation.db_recommendations import (
    generate_recommendations
)


def explain_recommendations():

    recommendations = (
        generate_recommendations()
    )

    results = []

    for rec in recommendations:

        probability = (
            rec["forget_probability"]
        )

        if probability > 0.8:

            reason = (
                "Very high probability of forgetting."
            )

        elif probability > 0.5:

            reason = (
                "Retention appears weak."
            )

        else:

            reason = (
                "Retention remains strong."
            )

        results.append(
            {
                "question":
                rec["title"],

                "forget_probability":
                probability,

                "explanation":
                reason
            }
        )

    return results