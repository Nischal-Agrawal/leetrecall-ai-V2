from fastapi import APIRouter

from backend.services.weak_topic_service import (
    get_weak_topics
)

router = APIRouter(
    prefix="/weak-topics",
    tags=["Weak Topics"]
)


@router.get("/")
def weak_topics():

    return get_weak_topics()