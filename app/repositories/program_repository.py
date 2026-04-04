from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.program_session import ProgramSession


class ProgramRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_available_dates(self) -> list[date]:
        stmt = (
            select(ProgramSession.session_date)
            .distinct()
            .order_by(ProgramSession.session_date.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_available_halls(self) -> list[dict]:
        stmt = select(ProgramSession.hall_code, ProgramSession.hall_name).distinct()
        rows = self.db.execute(stmt).all()

        hall_map = {row.hall_code: row.hall_name for row in rows}
        ordered_codes = [
            "main",
            "financial-games",
            "transaction-constructor",
            "brand-zone",
        ]

        result = []
        for code in ordered_codes:
            if code in hall_map:
                result.append({"code": code, "name": hall_map[code]})

        return result

    def get_sessions(self, *, session_date: date, hall_code: str) -> list[ProgramSession]:
        stmt = (
            select(ProgramSession)
            .where(
                ProgramSession.session_date == session_date,
                ProgramSession.hall_code == hall_code,
            )
            .order_by(ProgramSession.start_time.asc(), ProgramSession.sort_order.asc())
        )
        return list(self.db.scalars(stmt).all())