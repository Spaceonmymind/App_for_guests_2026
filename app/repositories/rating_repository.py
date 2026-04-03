from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.user_activity import UserActivity


class RatingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_leaderboard(self) -> list[dict]:
        stmt = (
            select(
                User.id.label("user_id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                User.code.label("code"),
                func.coalesce(func.sum(UserActivity.points), 0).label("total_points"),
            )
            .outerjoin(UserActivity, UserActivity.user_id == User.id)
            .where(User.role == UserRole.PARTICIPANT.value)
            .group_by(User.id, User.first_name, User.last_name, User.code)
            .order_by(
                func.coalesce(func.sum(UserActivity.points), 0).desc(),
                User.last_name.asc(),
                User.first_name.asc(),
                User.id.asc(),
            )
        )

        rows = self.db.execute(stmt).all()

        leaderboard: list[dict] = []
        for index, row in enumerate(rows, start=1):
            leaderboard.append(
                {
                    "place": index,
                    "user_id": row.user_id,
                    "first_name": row.first_name or "",
                    "last_name": row.last_name or "",
                    "code": row.code,
                    "total_points": row.total_points or 0,
                }
            )

        return leaderboard