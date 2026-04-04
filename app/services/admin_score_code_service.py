from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.score_code_service import ScoreCodeService


class AdminScoreCodeError(Exception):
    pass


class AdminScoreCodeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def regenerate(self, *, user_id: int) -> str:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise AdminScoreCodeError("Пользователь не найден.")

        if user.role != UserRole.PARTICIPANT.value:
            raise AdminScoreCodeError("Короткий код можно пересоздавать только участнику.")

        user.score_code = None
        self.db.commit()

        new_code = ScoreCodeService(self.user_repo).generate_unique()
        user.score_code = new_code
        self.db.commit()

        return new_code