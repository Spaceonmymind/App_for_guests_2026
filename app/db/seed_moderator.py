from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserActivationStatus, UserRole

MODERATORS = [
    {"code": "MOD309", "first_name": "Маша", "last_name": "Хомякова"},
    {"code": "MOD630", "first_name": "Егор", "last_name": "Гладких"},
    {"code": "MOD136", "first_name": "Юлия", "last_name": "Дюкина"},
    {"code": "MOD683", "first_name": "Маша", "last_name": "Афанасьева"},
    {"code": "MOD591", "first_name": "Аня", "last_name": "Гусева"},
    {"code": "MOD090", "first_name": "Андрей", "last_name": "Лушин"},
    {"code": "MOD703", "first_name": "Виктория", "last_name": "Петренко"},
    {"code": "MOD778", "first_name": "Маша", "last_name": "Дятлова"},
    {"code": "MOD119", "first_name": "Никита", "last_name": "Колесников"},
    {"code": "MOD210", "first_name": "Евгений", "last_name": "Киселев"},
    {"code": "MOD411", "first_name": "Катя", "last_name": "Пинясова"},
    {"code": "MOD431", "first_name": "Арина", "last_name": "Непомнящая"},
    {"code": "MOD513", "first_name": "Зоя", "last_name": "Комарова"},
    {"code": "MOD154", "first_name": "Арина", "last_name": "Полонец"},
    {"code": "MOD134", "first_name": "Анна", "last_name": "Головань"},
    {"code": "MOD579", "first_name": "Соня-Милана", "last_name": "Заева"},
    {"code": "MOD216", "first_name": "Модератор", "last_name": "Квиз"},
    {"code": "MOD911", "first_name": "Модератор", "last_name": "Прожарка"},
]



def seed() -> None:
    with SessionLocal() as db:
        existing_codes = set(db.scalars(select(User.code)).all())
        created = 0

        for item in MODERATORS:
            if item["code"] in existing_codes:
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