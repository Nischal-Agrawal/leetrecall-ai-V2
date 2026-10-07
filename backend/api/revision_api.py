from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.models.revision import Revision

from backend.schemas.revision_schema import (
    RevisionCreate,
    RevisionResponse
)

router = APIRouter(
    prefix="/revisions",
    tags=["Revisions"]
)


@router.post(
    "/",
    response_model=RevisionResponse
)
def create_revision(
    revision: RevisionCreate,
    db: Session = Depends(get_db)
):
    db_revision = Revision(
        user_id=revision.user_id,
        question_id=revision.question_id,
        revision_quality=revision.revision_quality
    )

    db.add(db_revision)

    db.commit()

    db.refresh(db_revision)

    return db_revision


@router.get("/")
def get_revisions(
    db: Session = Depends(get_db)
):
    return db.query(Revision).all()