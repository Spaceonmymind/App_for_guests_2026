from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feature_flags import FeatureFlags


class FeatureFlagsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create(self) -> FeatureFlags:
        flags = self.db.scalar(select(FeatureFlags))
        if flags is None:
            flags = FeatureFlags()
            self.db.add(flags)
            self.db.commit()
            self.db.refresh(flags)
        return flags

    def set_master_poll_open(self, value: bool) -> FeatureFlags:
        flags = self.get_or_create()
        flags.is_master_poll_open = value
        self.db.commit()
        self.db.refresh(flags)
        return flags

    def set_project_voting_open(self, value: bool) -> FeatureFlags:
        flags = self.get_or_create()
        flags.is_project_voting_open = value
        self.db.commit()
        self.db.refresh(flags)
        return flags