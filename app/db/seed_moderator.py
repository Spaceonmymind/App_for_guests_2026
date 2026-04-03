from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserActivationStatus, UserRole


def seed() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.code == "99999"))
        if existing is None:
            db.add(
                User(
                    code="99999",
                    first_name="Тестовый",
                    last_name="Модератор",
                    role=UserRole.MODERATOR.value,
                    activation_status=UserActivationStatus.ACTIVE.value,
                )
            )
            db.commit()
            print("Moderator created: 99999")
        else:
            print("Moderator already exists.")


if __name__ == "__main__":
    seed()