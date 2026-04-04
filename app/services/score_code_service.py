import random

from app.repositories.user_repository import UserRepository


class ScoreCodeService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def generate_unique(self) -> str:
        for _ in range(2000):
            code = str(random.randint(100, 999))
            existing = self.user_repo.get_by_score_code(code)
            if existing is None:
                return code

        raise ValueError("Не удалось сгенерировать уникальный код участника")