from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.voting_project import VotingProject


class VotingProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_projects(self) -> list[VotingProject]:
        stmt = (
            select(VotingProject)
            .where(VotingProject.is_active.is_(True))
            .order_by(VotingProject.sort_order.asc(), VotingProject.id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, project_id: int) -> VotingProject | None:
        stmt = select(VotingProject).where(VotingProject.id == project_id)
        return self.db.scalar(stmt)