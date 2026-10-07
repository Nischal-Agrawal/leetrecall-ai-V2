def generate_explanation(
    title,
    forget_probability,
    confidence_score,
    revision_count
):

    reasons = []

    if forget_probability > 0.7:
        reasons.append(
            "high forget probability"
        )

    if confidence_score < 5:
        reasons.append(
            "low confidence score"
        )

    if revision_count == 0:
        reasons.append(
            "no revisions recorded"
        )

    if not reasons:
        reasons.append(
            "retention remains strong"
        )

    explanation = (
        f"{title} analysis:\n\n"
    )

    for reason in reasons:

        explanation += (
            f"• {reason}\n"
        )

    return explanation