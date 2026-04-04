from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserActivationStatus, UserRole

ADMINS = [
    {"code": "900001", "first_name": "Админ", "last_name": "Основной"},
]


def seed() -> None:
    with SessionLocal() as db:
        created = 0

        for item in ADMINS:
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
                    role=UserRole.ADMIN.value,
                    activation_status=UserActivationStatus.ACTIVE.value,
                )
            )
            created += 1

        db.commit()
        print(f"Created admins: {created}")


if __name__ == "__main__":
    seed()