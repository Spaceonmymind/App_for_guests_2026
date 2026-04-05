from sqlalchemy.orm import Session

from app.models.user import UserActivationStatus, UserRole
from app.repositories.activity_repository import ActivityRepository
from app.repositories.moderator_activity_repository import ModeratorActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository
from app.repositories.user_repository import UserRepository
from app.services.moderator_activity_rules import get_allowed_award_types


class ModeratorAwardError(Exception):
    pass


class ModeratorAwardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.moderator_activity_repo = ModeratorActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def award(
        self,
        *,
        moderator_user_id: int,
        participant_code: str,
        activity_id: int,
        award_type: str,
    ) -> None:
        moderator = self.user_repo.get_by_id(moderator_user_id)
        if moderator is None:
            raise ModeratorAwardError("Модератор не найден.")

        if moderator.role not in {UserRole.MODERATOR.value, UserRole.ADMIN.value}:
            raise ModeratorAwardError("Нет доступа к начислению баллов.")

        allowed_activity_ids = set(
            self.moderator_activity_repo.get_activity_ids_for_moderator(
                moderator_user_id=moderator.id
            )
        )
        if activity_id not in allowed_activity_ids:
            raise ModeratorAwardError("Эта активность вам недоступна.")

        activity = self.activity_repo.get_by_id(activity_id)
        if activity is None:
            raise ModeratorAwardError("Активность не найдена.")

        participant = self.user_repo.get_by_score_code(participant_code)
        if participant is None:
            raise ModeratorAwardError("Участник с таким кодом не найден.")

        if participant.role != UserRole.PARTICIPANT.value:
            raise ModeratorAwardError("Баллы можно начислять только участникам.")

        if participant.activation_status != UserActivationStatus.ACTIVE.value:
            raise ModeratorAwardError("Участник не активирован.")

        allowed_award_types = set(get_allowed_award_types(activity.name))
        if award_type not in allowed_award_types:
            raise ModeratorAwardError("Для этой активности такой тип начисления недоступен.")

        all_awards = self.user_activity_repo.get_awards_for_user_activity(
            user_id=participant.id,
            activity_id=activity.id,
        )

        existing_award_types = {item.award_type for item in all_awards}

        if award_type in existing_award_types:
            raise ModeratorAwardError("Такое начисление этому участнику уже было сделано.")

        if award_type == "winner" and "participation" in existing_award_types:
            raise ModeratorAwardError("Нельзя начислить победу: участнику уже начислено участие.")

        if award_type == "participation" and "winner" in existing_award_types:
            raise ModeratorAwardError("Нельзя начислить участие: участнику уже начислена победа.")

        points = self._get_points(activity=activity, award_type=award_type)

        self.user_activity_repo.create(
            user_id=participant.id,
            activity_id=activity.id,
            award_type=award_type,
            points=points,
            awarded_by_user_id=moderator.id,
        )

    def _get_points(self, *, activity, award_type: str) -> int:
        if award_type == "participation":
            return activity.points_participation

        if award_type == "winner":
            return activity.points_win

        if award_type == "assembly":
            return activity.points_participation

        raise ModeratorAwardError("Не удалось определить количество баллов.")