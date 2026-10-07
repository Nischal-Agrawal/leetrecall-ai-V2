from backend.services.topic_mastery_service import (
    calculate_topic_mastery
)


def get_weak_topics():

    topics = calculate_topic_mastery()

    topics.sort(
        key=lambda x: x["mastery"]
    )

    return topics[:5]