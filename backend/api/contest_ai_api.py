from fastapi import APIRouter

from backend.services.contest_ai_service import (
    generate_contest_review
)

router = APIRouter(
    prefix="/contest-ai",
    tags=["Contest AI"]
)


@router.get("/")
def contest_ai():

    return generate_contest_review()