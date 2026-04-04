from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rating_settings import RatingSettings


class RatingSettingsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self) -> RatingSettings:
        stmt = select(RatingSettings).limit(1)
        settings = self.db.scalar(stmt)

        if settings is None:
            settings = RatingSettings()
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return settings

    def save(self, settings: RatingSettings) -> RatingSettings:
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings