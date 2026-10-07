from pydantic import BaseModel


class RevisionCreate(BaseModel):
    user_id: int
    question_id: int
    revision_quality: float


class RevisionResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    revision_quality: float

    class Config:
        from_attributes = True