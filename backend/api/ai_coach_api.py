from fastapi import APIRouter

from backend.services.recommendation_explainer import (
    explain_recommendations
)

router = APIRouter(
    prefix="/ai-coach",
    tags=["AI Coach"]
)


@router.get("/recommendations")
def explain():

    return explain_recommendations()