from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserActivationStatus, UserRole

MODERATORS = [
    {"code": "11111", "first_name": "Модератор", "last_name": "Егор"},
    {"code": "22222", "first_name": "Модератор", "last_name": "Ваня"},
    {"code": "33333", "first_name": "Модератор", "last_name": "Петя"},
]


def seed() -> None:
    with SessionLocal() as db:
        created = 0

        for item in MODERATORS:
            existing = db.scalar(
                select(User).where(User.code == item["code"])
            )
            if existing is not None:
                continue

            db.add(
                User(
                    code=item["code"],
                    first_name=item["first_name"],
                    last_name=item["last_name"],
                    role=UserRole.MODERATOR.value,
                    activation_status=UserActivationStatus.ACTIVE.value,
                )
            )
            created += 1

        db.commit()
        print(f"Created moderators: {created}")


if __name__ == "__main__":
    seed()