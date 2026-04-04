from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserActivationStatus, UserRole

TEST_CODES = [
    "A7K91Q",
    "ZX4P82L",
    "QW91ER7",
    "PLM8K23",
    "RT56YU9",
]


def seed_users() -> None:
    with SessionLocal() as db:
        existing_codes = set(db.scalars(select(User.code)).all())

        created_count = 0

        for code in TEST_CODES:
            if code in existing_codes:
                continue

            user = User(
                code=code,
                role=UserRole.PARTICIPANT.value,
                activation_status=UserActivationStatus.PENDING.value,
            )
            db.add(user)
            created_count += 1

        db.commit()
        print(f"Seed completed. Created users: {created_count}")


if __name__ == "__main__":
    seed_users()