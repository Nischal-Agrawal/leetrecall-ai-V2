from fastapi import APIRouter, Query

from backend.services.interview_ai_service import (
    generate_ai_interview_plan,
)

router = APIRouter(
    prefix="/interview-ai",
    tags=["AI Interview Planner"],
)


@router.get("/")
def interview_ai(
    interview_date: str = Query(
        ...,
        description="Interview date in YYYY-MM-DD format",
        example="2026-07-15",
    )
):
    return generate_ai_interview_plan(
        interview_date
    )