from fastapi import APIRouter

from backend.services.weak_pattern_service import (
    get_weak_patterns
)

router = APIRouter(
    prefix="/weak-patterns",
    tags=["Weak Patterns"]
)


@router.get("/")
def weak_patterns():

    return get_weak_patterns()