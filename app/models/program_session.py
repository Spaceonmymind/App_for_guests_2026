from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ProgramSession(Base):
    __tablename__ = "program_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hall_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    hall_name: Mapped[str] = mapped_column(String(255), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    section_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)