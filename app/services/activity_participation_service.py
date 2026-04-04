from sqlalchemy.orm import Session

from app.repositories.activity_participation_repository import ActivityParticipationRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository


class ActivityParticipationError(Exception):
    pass


class ActivityParticipationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.participation_repo = ActivityParticipationRepository(db)

    def join_activity(
        self,
        *,
        user_id: int,
        activity_id: int,
    ) -> None:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise ActivityParticipationError("Пользователь не найден.")

        activity = self.activity_repo.get_by_id(activity_id)
        if activity is None:
            raise ActivityParticipationError("Активность не найдена.")

        existing = self.participation_repo.get_by_user_and_activity(
            user_id=user_id,
            activity_id=activity_id,
        )
        if existing is not None:
            raise ActivityParticipationError("Вы уже отметили участие в этой активности.")

        self.participation_repo.create(
            user_id=user_id,
            activity_id=activity_id,
        )