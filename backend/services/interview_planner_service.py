from datetime import datetime

from backend.services.weak_topic_service import (
    get_weak_topics,
)

from backend.services.weak_pattern_service import (
    get_weak_patterns,
)


def generate_interview_plan(interview_date: str):
    """
    Generate a basic interview revision plan.
    interview_date format:
    YYYY-MM-DD
    """

    interview = datetime.strptime(
        interview_date,
        "%Y-%m-%d",
    )

    today = datetime.today()

    days_remaining = (
        interview - today
    ).days

    weak_topics = get_weak_topics()

    weak_patterns = get_weak_patterns()

    return {
        "interview_date": interview_date,
        "days_remaining": days_remaining,
        "weak_topics": weak_topics,
        "weak_patterns": weak_patterns,
    }