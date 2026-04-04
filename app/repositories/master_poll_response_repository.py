from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master_poll_response import MasterPollResponse


class MasterPollResponseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, *, user_id: int) -> MasterPollResponse | None:
        stmt = select(MasterPollResponse).where(MasterPollResponse.user_id == user_id)
        return self.db.scalar(stmt)

    def create(self, *, user_id: int, answers_json: str) -> MasterPollResponse:
        response = MasterPollResponse(
            user_id=user_id,
            answers_json=answers_json,
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response