from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vote import Vote


class VoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_vote(self, *, user_id: int) -> Vote | None:
        stmt = select(Vote).where(Vote.user_id == user_id)
        return self.db.scalar(stmt)

    def create(self, *, user_id: int, project_id: int) -> Vote:
        vote = Vote(user_id=user_id, project_id=project_id)
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote