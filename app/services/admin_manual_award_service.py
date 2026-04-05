from sqlalchemy.orm import Session

from app.models.user import UserActivationStatus, UserRole
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_manual_award_rules import get_admin_award_options


class AdminManualAwardError(Exception):
    pass


class AdminManualAwardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def apply(
        self,
        *,
        admin_user_id: int,
        participant_code: str,
        activity_id: int,
        award_type: str,
        operation: str,
    ) -> int:
        admin = self.user_repo.get_by_id(admin_user_id)
        if admin is None or admin.role != UserRole.ADMIN.value:
            raise AdminManualAwardError("Нет доступа к ручной корректировке баллов.")

        participant = self.user_repo.get_by_score_code(participant_code)
        if participant is None:
            raise AdminManualAwardError("Участник с таким кодом не найден.")

        if participant.role != UserRole.PARTICIPANT.value:
            raise AdminManualAwardError("Корректировка доступна только для участников.")

        if participant.activation_status != UserActivationStatus.ACTIVE.value:
            raise AdminManualAwardError("Участник не активирован.")

        activity = self.activity_repo.get_by_id(activity_id)
        if activity is None:
            raise AdminManualAwardError("Активность не найдена.")

        award_options = get_admin_award_options(activity.name)
        option_map = {item["value"]: item for item in award_options}

        selected_option = option_map.get(award_type)
        if selected_option is None:
            raise AdminManualAwardError("Для этой активности такой тип операции недоступен.")

        if selected_option["points_source"] == "points_win":
            points = activity.points_win
        else:
            points = activity.points_participation

        if operation == "subtract":
            points = -points
            internal_award_type = f"admin_subtract_{award_type}"
        elif operation == "add":
            internal_award_type = f"admin_add_{award_type}"
        else:
            raise AdminManualAwardError("Неизвестный тип операции.")

        self.user_activity_repo.create(
            user_id=participant.id,
            activity_id=activity.id,
            award_type=internal_award_type,
            points=points,
            awarded_by_user_id=admin.id,
        )

        return points