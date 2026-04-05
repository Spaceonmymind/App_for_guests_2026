from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.fin_game_vote import FinGameVote


class FinGameVoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_vote(self, *, user_id: int) -> FinGameVote | None:
        stmt = select(FinGameVote).where(FinGameVote.user_id == user_id)
        return self.db.scalar(stmt)

    def create(self, *, user_id: int, activity_id: int) -> FinGameVote:
        vote = FinGameVote(user_id=user_id, activity_id=activity_id)
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def get_results(self) -> list[dict]:
        stmt = (
            select(
                Activity.id,
                Activity.name,
                func.count(FinGameVote.id).label("votes_count"),
            )
            .join(FinGameVote, FinGameVote.activity_id == Activity.id, isouter=True)
            .where(
                Activity.name.in_(
                    [
                        "Юный инвестор",
                        "Инновационный ширпотреб",
                        "Финансовый детектив",
                        "Накопи на мечту",
                        "Мамин инвестор",
                        "Жажда власти",
                    ]
                )
            )
            .group_by(Activity.id, Activity.name)
            .order_by(func.count(FinGameVote.id).desc(), Activity.name.asc())
        )

        rows = self.db.execute(stmt).all()

        total_votes = sum(row.votes_count for row in rows)

        results = []
        for row in rows:
            percent = round((row.votes_count / total_votes) * 100) if total_votes > 0 else 0
            results.append(
                {
                    "activity_id": row.id,
                    "name": row.name,
                    "votes_count": row.votes_count,
                    "percent": percent,
                }
            )

        return results