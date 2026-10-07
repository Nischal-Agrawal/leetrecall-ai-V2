from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func

from backend.database.base import Base


class Solve(Base):

    __tablename__ = "solves"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    solved_at = Column(
        DateTime,
        server_default=func.now()
    )

    time_taken_minutes = Column(Integer)

    wrong_attempts = Column(Integer)

    hints_used = Column(Integer)

    confidence_score = Column(Float)