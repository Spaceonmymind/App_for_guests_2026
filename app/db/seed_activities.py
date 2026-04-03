from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.activity import Activity

ACTIVITIES = [
    "Финансовая игра 1",
    "Финансовая игра 2",
    "Финансовая игра 3",
    "Финансовая игра 4",
    "Финансовая игра 5",
    "Финансовая игра 6",
    "Конструктор транзакций 1",
    "Конструктор транзакций 2",
    "Конструктор транзакций 3",
    "Конструктор транзакций 4",
    "Финтех-гуру",
    "Мир идей",
    "Квиз",
    "Прожарка резюме",
]


def seed() -> None:
    with SessionLocal() as db:
        existing_names = set(db.scalars(select(Activity.name)).all())
        created = 0

        for name in ACTIVITIES:
            if name in existing_names:
                continue

            db.add(
                Activity(
                    name=name,
                    points_participation=5,
                    points_win=10,
                )
            )
            created += 1

        db.commit()
        print(f"Created activities: {created}")


if __name__ == "__main__":
    seed()