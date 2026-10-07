from fastapi import APIRouter

from backend.services.dynamic_ai_coach import (
    get_dynamic_advice
)

router = APIRouter(
    prefix="/dynamic-ai-coach",
    tags=["Dynamic AI Coach"]
)


@router.get("/")
def dynamic_coach():

    return get_dynamic_advice()