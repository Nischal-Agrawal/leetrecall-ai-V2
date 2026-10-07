from fastapi import APIRouter, Query

from backend.services.interview_planner_service import (
    generate_interview_plan,
)

router = APIRouter(
    prefix="/interview-mode",
    tags=["Interview Mode"],
)


@router.get("/")
def interview_mode(
    interview_date: str = Query(
        ...,
        description="Interview date in YYYY-MM-DD format",
        example="2026-07-15",
    )
):
    return generate_interview_plan(
        interview_date
    )