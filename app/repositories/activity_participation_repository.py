from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_participation import ActivityParticipation


class ActivityParticipationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_and_activity(
        self,
        *,
        user_id: int,
        activity_id: int,
    ) -> ActivityParticipation | None:
        stmt = select(ActivityParticipation).where(
            ActivityParticipation.user_id == user_id,
            ActivityParticipation.activity_id == activity_id,
        )
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        user_id: int,
        activity_id: int,
    ) -> ActivityParticipation:
        record = ActivityParticipation(
            user_id=user_id,
            activity_id=activity_id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_activity_ids_for_user(self, *, user_id: int) -> set[int]:
        stmt = select(ActivityParticipation.activity_id).where(
            ActivityParticipation.user_id == user_id,
        )
        return set(self.db.scalars(stmt).all())