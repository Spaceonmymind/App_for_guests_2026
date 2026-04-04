from sqlalchemy import select
from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        stmt = select(Activity).order_by(Activity.id)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, activity_id: int):
        stmt = select(Activity).where(Activity.id == activity_id)
        return self.db.scalar(stmt)