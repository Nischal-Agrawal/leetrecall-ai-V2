from fastapi import APIRouter

from backend.services.topic_mastery_service import (
    calculate_topic_mastery
)

router = APIRouter(
    prefix="/topic-mastery",
    tags=["Topic Mastery"]
)


@router.get("/")
def get_topic_mastery():

    return calculate_topic_mastery()