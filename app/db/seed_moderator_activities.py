from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.moderator_activity import ModeratorActivity
from app.models.user import User

BINDINGS = [
    {
        "moderator_code": "111111",
        "activity_names": [
            "Юный инвестор",
        ],
    },
    {
        "moderator_code": "222222",
        "activity_names": [
            "Финансовый детектив",
        ],
    },
    {
        "moderator_code": "333333",
        "activity_names": [
            "ПС Мир",
            "Блокчейн",
        ],
    },
]


def seed() -> None:
    with SessionLocal() as db:
        created = 0

        for binding in BINDINGS:
            moderator = db.scalar(
                select(User).where(User.code == binding["moderator_code"])
            )
            if moderator is None:
                print(f"Moderator not found: {binding['moderator_code']}")
                continue

            for activity_name in binding["activity_names"]:
                activity = db.scalar(
                    select(Activity).where(Activity.name == activity_name)
                )
                if activity is None:
                    print(f"Activity not found: {activity_name}")
                    continue

                existing = db.scalar(
                    select(ModeratorActivity).where(
                        ModeratorActivity.moderator_user_id == moderator.id,
                        ModeratorActivity.activity_id == activity.id,
                    )
                )
                if existing is not None:
                    continue

                db.add(
                    ModeratorActivity(
                        moderator_user_id=moderator.id,
                        activity_id=activity.id,
                    )
                )
                created += 1

        db.commit()
        print(f"Created moderator activity bindings: {created}")


if __name__ == "__main__":
    seed()