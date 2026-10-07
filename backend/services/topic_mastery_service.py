from collections import defaultdict

from backend.database.connection import SessionLocal

from backend.models.question import Question
from backend.models.solve import Solve
from backend.models.revision import Revision


def calculate_topic_mastery():

    db = SessionLocal()

    questions = db.query(
        Question
    ).all()

    solves = db.query(
        Solve
    ).all()

    revisions = db.query(
        Revision
    ).all()

    topic_total = defaultdict(int)

    topic_score = defaultdict(int)

    question_topic = {}

    for question in questions:

        topic = question.topic

        topic_total[topic] += 1

        question_topic[
            question.id
        ] = topic

    for solve in solves:

        topic = question_topic.get(
            solve.question_id
        )

        if topic:

            topic_score[topic] += 1

    for revision in revisions:

        topic = question_topic.get(
            revision.question_id
        )

        if topic:

            topic_score[topic] += 1

    results = []

    for topic in topic_total:

        mastery = (
            topic_score[topic]
            /
            topic_total[topic]
        ) * 100

        results.append(
            {
                "topic": topic,
                "mastery": round(
                    mastery,
                    2
                )
            }
        )

    db.close()

    return results
