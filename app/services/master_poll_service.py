import json

from sqlalchemy.orm import Session

from app.repositories.activity_repository import ActivityRepository
from app.repositories.master_poll_response_repository import MasterPollResponseRepository
from app.repositories.user_activity_repository import UserActivityRepository


class MasterPollError(Exception):
    pass


class MasterPollService:
    MASTER_POLL_ACTIVITY_NAME = "Мастер-опрос"
    MASTER_POLL_POINTS = 10
    MASTER_POLL_AWARD_TYPE = "master_poll"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.response_repo = MasterPollResponseRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def is_completed(self, *, user_id: int) -> bool:
        return self.response_repo.get_by_user_id(user_id=user_id) is not None

    def submit(self, *, user_id: int, answers: dict[str, str]) -> None:
        existing = self.response_repo.get_by_user_id(user_id=user_id)
        if existing is not None:
            raise MasterPollError("Вы уже прошли мастер-опрос.")

        activity = self.activity_repo.get_by_name(self.MASTER_POLL_ACTIVITY_NAME)
        if activity is None:
            raise MasterPollError("Активность 'Мастер-опрос' не найдена в базе.")

        existing_award = self.user_activity_repo.get_existing_award(
            user_id=user_id,
            activity_id=activity.id,
            award_type=self.MASTER_POLL_AWARD_TYPE,
        )
        if existing_award is not None:
            raise MasterPollError("Баллы за мастер-опрос уже начислены.")

        self.response_repo.create(
            user_id=user_id,
            answers_json=json.dumps(answers, ensure_ascii=False),
        )

        self.user_activity_repo.create(
            user_id=user_id,
            activity_id=activity.id,
            award_type=self.MASTER_POLL_AWARD_TYPE,
            points=self.MASTER_POLL_POINTS,
            awarded_by_user_id=user_id,
        )