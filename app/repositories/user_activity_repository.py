from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_activity import UserActivity


class UserActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_existing_award(
        self,
        *,
        user_id: int,
        activity_id: int,
        award_type: str,
    ) -> UserActivity | None:
        stmt = select(UserActivity).where(
            UserActivity.user_id == user_id,
            UserActivity.activity_id == activity_id,
            UserActivity.award_type == award_type,
        )
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        user_id: int,
        activity_id: int,
        award_type: str,
        points: int,
        awarded_by_user_id: int,
    ) -> UserActivity:
        record = UserActivity(
            user_id=user_id,
            activity_id=activity_id,
            award_type=award_type,
            points=points,
            awarded_by_user_id=awarded_by_user_id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record