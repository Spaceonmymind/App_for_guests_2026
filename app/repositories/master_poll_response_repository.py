import json
from collections import Counter

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

    def get_all(self) -> list[MasterPollResponse]:
        stmt = select(MasterPollResponse).order_by(MasterPollResponse.id.asc())
        return list(self.db.scalars(stmt).all())

    def get_answer_distribution(self) -> dict[str, Counter]:
        responses = self.get_all()
        distribution: dict[str, Counter] = {
            "1": Counter(),
            "2": Counter(),
            "3": Counter(),
            "4": Counter(),
        }

        for response in responses:
            try:
                answers = json.loads(response.answers_json)
            except Exception:
                continue

            for question_key in ("1", "2", "3", "4"):
                answer = answers.get(question_key)
                if answer:
                    distribution[question_key][answer] += 1

        return distribution