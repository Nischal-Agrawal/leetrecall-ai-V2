from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func

from backend.database.base import Base


class Question(Base):

    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    platform = Column(
        String(50),
        nullable=False
    )

    topic = Column(
        String(100),
        nullable=False
    )

    pattern = Column(
        String(100),
        nullable=False
    )

    difficulty = Column(
        String(20),
        nullable=False
    )

    tags = Column(Text)

    url = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )