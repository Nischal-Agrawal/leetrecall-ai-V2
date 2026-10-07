from fastapi import APIRouter

from backend.services.pattern_coverage_service import (
    calculate_pattern_coverage
)

router = APIRouter(
    prefix="/pattern-coverage",
    tags=["Pattern Coverage"]
)


@router.get("/")
def get_pattern_coverage():

    return calculate_pattern_coverage()