from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_code(self, code: str) -> User | None:
        stmt = select(User).where(func.upper(User.code) == code.upper())
        return self.db.scalar(stmt)

    def get_by_score_code(self, score_code: str):
        stmt = select(User).where(User.score_code == score_code)
        return self.db.scalar(stmt)

    def create(
        self,
        *,
        code: str,
        role: str = "participant",
        activation_status: str = "pending",
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        user = User(
            code=code,
            role=role,
            activation_status=activation_status,
            first_name=first_name,
            last_name=last_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def activate_user(
        self,
        *,
        user: User,
        first_name: str,
        last_name: str,
    ) -> User:
        user.first_name = first_name
        user.last_name = last_name
        user.activation_status = "active"
        user.activated_at = datetime.utcnow()

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user