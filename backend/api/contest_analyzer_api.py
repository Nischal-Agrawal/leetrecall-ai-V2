from fastapi import APIRouter

from backend.services.contest_analyzer_service import (
    analyze_contest
)

router = APIRouter(
    prefix="/contest-analyzer",
    tags=["Contest Analyzer"]
)


@router.get("/")
def contest_analyzer():

    return analyze_contest()