from pydantic import BaseModel
from typing import Optional


class QuestionCreate(BaseModel):
    title: str
    platform: str
    topic: str
    pattern: str
    difficulty: str
    tags: Optional[str] = None
    url: Optional[str] = None


class QuestionResponse(BaseModel):
    id: int
    title: str
    platform: str
    topic: str
    pattern: str
    difficulty: str
    tags: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True