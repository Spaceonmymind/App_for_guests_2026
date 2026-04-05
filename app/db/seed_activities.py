from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.activity import Activity

ACTIVITIES = [
    {"name": "Юный инвестор", "points_participation": 2, "points_win": 5},
    {"name": "Инновационный ширпотреб", "points_participation": 2, "points_win": 5},
    {"name": "Финансовый детектив", "points_participation": 2, "points_win": 5},
    {"name": "Накопи на мечту", "points_participation": 2, "points_win": 5},
    {"name": "Мамин инвестор", "points_participation": 2, "points_win": 5},
    {"name": "Жажда власти", "points_participation": 2, "points_win": 5},

    {"name": "ПС Мир", "points_participation": 5, "points_win": 5},
    {"name": "СБП", "points_participation": 5, "points_win": 5},
    {"name": "Блокчейн", "points_participation": 5, "points_win": 5},
    {"name": "3D-Secure", "points_participation": 5, "points_win": 5},

    {"name": "Финтех-гуру", "points_participation": 2, "points_win": 5},
    {"name": "Мир идей", "points_participation": 2, "points_win": 5},
    {"name": "Квиз Мир Plat.Form", "points_participation": 2, "points_win": 5},
    {"name": "Прожарка резюме", "points_participation": 2, "points_win": 5},

    {"name": "Мастер-опрос", "points_participation": 10, "points_win": 10},
    {"name": "Голосование за лучший проект", "points_participation": 10, "points_win": 10},
]


def seed() -> None:
    with SessionLocal() as db:
        existing_names = set(db.scalars(select(Activity.name)).all())
        created = 0

        for item in ACTIVITIES:
            name = item["name"]

            if name in existing_names:
                continue

            db.add(
                Activity(
                    name=name,
                    points_participation=item["points_participation"],
                    points_win=item["points_win"],
                )
            )
            created += 1

        db.commit()
        print(f"Created activities: {created}")


if __name__ == "__main__":
    seed()