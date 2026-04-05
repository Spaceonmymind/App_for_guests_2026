from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.moderator_activity import ModeratorActivity
from app.models.user import User, UserRole



MODERATOR_BINDINGS = {
    "Маша Хомякова": ["Мир идей"],
    "Егор Гладких": "__ALL__",
    "Юлия Дюкина": "__ALL__",
    "Маша Афанасьева": ["ПС Мир", "СБП", "Блокчейн", "3D-Secure"],
    "Аня Гусева": ["ПС Мир", "СБП", "Блокчейн", "3D-Secure"],
    "Андрей Лушин": ["ПС Мир"],
    "Виктория Петренко": ["3D-Secure"],
    "Маша Дятлова": ["Блокчейн"],
    "Никита Колесников": ["Финтех-гуру", "Мир идей", "Прожарка резюме", "Квиз Мир Plat.Form", "Мастер-опрос"],
    "Евгений Киселев": ["Инновационный ширпотреб"],
    "Катя Пинясова": ["Жажда власти"],
    "Арина Непомнящая": ["Юный инвестор"],
    "Зоя Комарова": ["Финансовый детектив"],
    "Арина Полонец": ["Накопи на мечту"],
    "Соня-Милана Заева": ["Мамин инвестор"],
    "Модератор Квиз": ["Квиз Мир Plat.Form"],
    "Модератор Прожарка": ["Прожарка резюме"],
}


def get_moderator_by_full_name(db, full_name: str) -> User | None:
    parts = full_name.split(" ", 1)
    if len(parts) != 2:
        return None

    first_name, last_name = parts
    return db.scalar(
        select(User).where(
            User.first_name == first_name,
            User.last_name == last_name,
            User.role == UserRole.MODERATOR.value,
        )
    )


def seed() -> None:
    with SessionLocal() as db:
        all_activities = list(db.scalars(select(Activity)).all())
        activities_by_name = {activity.name: activity for activity in all_activities}

        existing_bindings = {
            (binding.moderator_user_id, binding.activity_id)
            for binding in db.scalars(select(ModeratorActivity)).all()
        }

        created = 0

        for moderator_name, binding_value in MODERATOR_BINDINGS.items():
            moderator = get_moderator_by_full_name(db, moderator_name)
            if moderator is None:
                print(f"Moderator not found: {moderator_name}")
                continue

            if binding_value == "__ALL__":
                target_activities = all_activities
            else:
                target_activities = []
                for activity_name in binding_value:
                    activity = activities_by_name.get(activity_name)
                    if activity is None:
                        print(f"Activity not found for {moderator_name}: {activity_name}")
                        continue
                    target_activities.append(activity)

            for activity in target_activities:
                key = (moderator.id, activity.id)
                if key in existing_bindings:
                    continue

                db.add(
                    ModeratorActivity(
                        moderator_user_id=moderator.id,
                        activity_id=activity.id,
                    )
                )
                existing_bindings.add(key)
                created += 1

        db.commit()
        print(f"Created moderator activity bindings: {created}")


if __name__ == "__main__":
    seed()