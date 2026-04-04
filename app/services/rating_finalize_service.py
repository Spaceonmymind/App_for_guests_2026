from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.rating_repository import RatingRepository
from app.repositories.rating_settings_repository import RatingSettingsRepository
from app.repositories.rating_winner_repository import RatingWinnerRepository
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole


class RatingFinalizeError(Exception):
    pass


class RatingFinalizeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.rating_repo = RatingRepository(db)
        self.settings_repo = RatingSettingsRepository(db)
        self.winner_repo = RatingWinnerRepository(db)
        self.user_repo = UserRepository(db)

    def finalize(self, *, admin_user_id: int) -> None:
        admin = self.user_repo.get_by_id(admin_user_id)
        if admin is None:
            raise RatingFinalizeError("Пользователь не найден.")

        if admin.role != UserRole.ADMIN.value:
            raise RatingFinalizeError("Только администратор может завершить рейтинг.")

        leaderboard = self.rating_repo.get_leaderboard()
        top_15 = leaderboard[:15]

        settings = self.settings_repo.get_or_create()

        self.winner_repo.delete_all()

        for item in top_15:
            self.winner_repo.create(
                user_id=item["user_id"],
                place=item["place"],
            )

        settings.is_finalized = True
        settings.finalized_at = datetime.utcnow()
        settings.finalized_by_user_id = admin.id
        self.settings_repo.save(settings)