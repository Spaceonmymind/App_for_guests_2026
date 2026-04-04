from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.moderator_activity import ModeratorActivity
from app.models.activity import Activity


class ModeratorActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_activity_ids_for_moderator(self, *, moderator_user_id: int) -> list[int]:
        stmt = (
            select(ModeratorActivity.activity_id)
            .where(ModeratorActivity.moderator_user_id == moderator_user_id)
            .order_by(ModeratorActivity.activity_id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_activities_for_moderator(self, *, moderator_user_id: int) -> list[Activity]:
        stmt = (
            select(Activity)
            .join(ModeratorActivity, ModeratorActivity.activity_id == Activity.id)
            .where(ModeratorActivity.moderator_user_id == moderator_user_id)
            .order_by(Activity.id.asc())
        )
        return list(self.db.scalars(stmt).all())