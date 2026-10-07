from fastapi import APIRouter

from backend.services.openai_coach import (
    generate_ai_advice
)

router = APIRouter(
    prefix="/openai-coach",
    tags=["OpenAI Coach"]
)


@router.get("/")
def ai_coach():

    advice = generate_ai_advice(
        question="3Sum",
        forget_probability=0.91
    )

    return {
        "advice": advice
    }