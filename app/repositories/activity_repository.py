from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Activity]:
        stmt = select(Activity).order_by(Activity.id.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, activity_id: int) -> Activity | None:
        return self.db.get(Activity, activity_id)