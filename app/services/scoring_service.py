from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository
from app.repositories.user_repository import UserRepository


class ScoringError(Exception):
    pass


class ScoringService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def award_points(
        self,
        *,
        participant_code: str,
        activity_id: int,
        award_type: str,
        moderator_user_id: int,
    ) -> None:
        moderator = self.user_repo.get_by_id(moderator_user_id)
        if moderator is None:
            raise ScoringError("Модератор не найден.")

        if moderator.role not in {UserRole.MODERATOR.value, UserRole.ADMIN.value}:
            raise ScoringError("У вас нет прав на начисление баллов.")

        participant = self.user_repo.get_by_code(participant_code)
        if participant is None:
            raise ScoringError("Участник с таким кодом не найден.")

        if participant.role != UserRole.PARTICIPANT.value:
            raise ScoringError("Баллы можно начислять только участнику.")

        activity = self.activity_repo.get_by_id(activity_id)
        if activity is None:
            raise ScoringError("Активность не найдена.")

        if award_type not in {"participation", "winner"}:
            raise ScoringError("Некорректный тип начисления.")

        existing_award = self.user_activity_repo.get_existing_award(
            user_id=participant.id,
            activity_id=activity.id,
            award_type=award_type,
        )
        if existing_award is not None:
            if award_type == "participation":
                raise ScoringError("Баллы за участие по этой активности уже начислены.")
            raise ScoringError("Баллы за победу по этой активности уже начислены.")

        points = activity.points_participation if award_type == "participation" else activity.points_win

        self.user_activity_repo.create(
            user_id=participant.id,
            activity_id=activity.id,
            award_type=award_type,
            points=points,
            awarded_by_user_id=moderator.id,
        )