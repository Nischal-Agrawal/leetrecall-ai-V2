from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func

from backend.database.base import Base


class Revision(Base):

    __tablename__ = "revisions"

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

    revised_at = Column(
        DateTime,
        server_default=func.now()
    )

    revision_quality = Column(Float)