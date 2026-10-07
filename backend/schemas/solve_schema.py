from pydantic import BaseModel


class SolveCreate(BaseModel):
    user_id: int
    question_id: int
    time_taken_minutes: int
    wrong_attempts: int
    hints_used: int
    confidence_score: float


class SolveResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    time_taken_minutes: int
    wrong_attempts: int
    hints_used: int
    confidence_score: float

    class Config:
        from_attributes = True