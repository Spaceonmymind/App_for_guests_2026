from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FeatureFlags(Base):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_master_poll_open: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_project_voting_open: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)