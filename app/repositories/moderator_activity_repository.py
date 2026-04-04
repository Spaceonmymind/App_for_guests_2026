from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.moderator_activity import ModeratorActivity
from app.models.user import User


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

    def get_all_bindings(self) -> list[tuple[ModeratorActivity, User, Activity]]:
        stmt = (
            select(ModeratorActivity, User, Activity)
            .join(User, User.id == ModeratorActivity.moderator_user_id)
            .join(Activity, Activity.id == ModeratorActivity.activity_id)
            .order_by(User.last_name.asc(), User.first_name.asc(), Activity.name.asc())
        )
        return list(self.db.execute(stmt).all())

    def create(self, *, moderator_user_id: int, activity_id: int) -> ModeratorActivity:
        binding = ModeratorActivity(
            moderator_user_id=moderator_user_id,
            activity_id=activity_id,
        )
        self.db.add(binding)
        self.db.commit()
        self.db.refresh(binding)
        return binding

    def get_existing(self, *, moderator_user_id: int, activity_id: int) -> ModeratorActivity | None:
        stmt = select(ModeratorActivity).where(
            ModeratorActivity.moderator_user_id == moderator_user_id,
            ModeratorActivity.activity_id == activity_id,
        )
        return self.db.scalar(stmt)

    def delete_by_id(self, binding_id: int) -> bool:
        binding = self.db.get(ModeratorActivity, binding_id)
        if binding is None:
            return False

        self.db.delete(binding)
        self.db.commit()
        return True