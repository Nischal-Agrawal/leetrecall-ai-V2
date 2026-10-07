from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.models.user import User
from backend.models.question import Question
from backend.models.solve import Solve
from backend.models.revision import Revision

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db)
):

    total_users = db.query(User).count()

    total_questions = db.query(Question).count()

    total_solves = db.query(Solve).count()

    total_revisions = db.query(Revision).count()

    return {
        "total_users": total_users,
        "total_questions": total_questions,
        "total_solves": total_solves,
        "total_revisions": total_revisions
    }