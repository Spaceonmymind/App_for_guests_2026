from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.vote import Vote
from app.models.voting_project import VotingProject


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

    def get_results(self) -> list[dict]:
        stmt = (
            select(
                VotingProject.id.label("project_id"),
                VotingProject.participant_name.label("participant_name"),
                VotingProject.project_name.label("project_name"),
                VotingProject.description.label("description"),
                VotingProject.photo_url.label("photo_url"),
                func.count(Vote.id).label("votes_count"),
            )
            .select_from(VotingProject)
            .outerjoin(Vote, Vote.project_id == VotingProject.id)
            .where(VotingProject.is_active.is_(True))
            .group_by(
                VotingProject.id,
                VotingProject.participant_name,
                VotingProject.project_name,
                VotingProject.description,
                VotingProject.photo_url,
            )
            .order_by(
                func.count(Vote.id).desc(),
                VotingProject.sort_order.asc(),
                VotingProject.id.asc(),
            )
        )

        rows = self.db.execute(stmt).all()

        results = []
        for index, row in enumerate(rows, start=1):
            results.append(
                {
                    "place": index,
                    "project_id": row.project_id,
                    "participant_name": row.participant_name,
                    "project_name": row.project_name,
                    "description": row.description,
                    "photo_url": row.photo_url,
                    "votes_count": row.votes_count or 0,
                }
            )

        return results