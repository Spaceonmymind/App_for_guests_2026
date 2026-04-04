from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository


@dataclass
class ActivityTaskView:
    id: int
    title: str
    subtitle: str
    participation_points: int
    winner_points: int
    is_joined: bool


@dataclass
class ActivityCategoryView:
    slug: str
    title: str
    subtitle: str
    tasks_count: int
    completed_count: int
    tasks: list[ActivityTaskView]
    is_clickable: bool
    badge_mode: str  # "standard" | "constructor"


class ActivitiesCatalogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def _build_catalog(self, user_id: int) -> list[ActivityCategoryView]:
        activities = self.activity_repo.get_all()
        joined_ids = self.user_activity_repo.get_awarded_activity_ids_for_user(user_id=user_id)

        grouped: dict[str, ActivityCategoryView] = {
            "financial-games": ActivityCategoryView(
                slug="financial-games",
                title="Финансовые\nигры",
                subtitle="Зал финансовых\nигр",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=True,
                badge_mode="standard",
            ),
            "transaction-constructor": ActivityCategoryView(
                slug="transaction-constructor",
                title="Конструктор\nтранзакций",
                subtitle="Зал конструктора\nтранзакций",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=True,
                badge_mode="constructor",
            ),
            "fintech-guru": ActivityCategoryView(
                slug="fintech-guru",
                title="Финтех-гуру",
                subtitle="Бренд-зона\nНСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "ideas-world": ActivityCategoryView(
                slug="ideas-world",
                title="Мир идей",
                subtitle="Бренд-зона\nНСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "quiz": ActivityCategoryView(
                slug="quiz",
                title="Квиз Мир\nPlat.Form",
                subtitle="Бренд-зона\nНСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "resume-roast": ActivityCategoryView(
                slug="resume-roast",
                title="Прожарка\nрезюме",
                subtitle="Бренд-зона\nНСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
        }

        financial_titles = [
            "Финансовая игра 1",
            "Финансовая игра 2",
            "Финансовая игра 3",
            "Финансовая игра 4",
            "Финансовая игра 5",
            "Финансовая игра 6",
        ]
        financial_task_titles = [
            "Игра «Юный инвестор»",
            "Игра «Инновационный ширпотреб»",
            "Игра «Финансовый детектив»",
            "Игра «Накопи на мечту»",
            "Игра «Мамин инвестор»",
            "Игра «Жажда власти»",
        ]

        constructor_titles = [
            "Конструктор транзакций 1",
            "Конструктор транзакций 2",
            "Конструктор транзакций 3",
            "Конструктор транзакций 4",
        ]
        constructor_task_titles = [
            "ПС Мир",
            "СБП",
            "Блокчейн",
            "3D-Secure",
        ]

        financial_map = dict(zip(financial_titles, financial_task_titles))
        constructor_map = dict(zip(constructor_titles, constructor_task_titles))

        for activity in activities:
            is_joined = activity.id in joined_ids

            if activity.name in financial_map:
                category = grouped["financial-games"]
                task_title = financial_map[activity.name]
                subtitle = ""
            elif activity.name in constructor_map:
                category = grouped["transaction-constructor"]
                task_title = constructor_map[activity.name]
                subtitle = ""
            elif activity.name == "Финтех-гуру":
                category = grouped["fintech-guru"]
                task_title = "Финтех-гуру"
                subtitle = ""
            elif activity.name == "Мир идей":
                category = grouped["ideas-world"]
                task_title = "Мир идей"
                subtitle = ""
            elif activity.name == "Квиз":
                category = grouped["quiz"]
                task_title = "Квиз Мир Plat.Form"
                subtitle = ""
            elif activity.name == "Прожарка резюме":
                category = grouped["resume-roast"]
                task_title = "Прожарка резюме"
                subtitle = ""
            else:
                continue

            category.tasks.append(
                ActivityTaskView(
                    id=activity.id,
                    title=task_title,
                    subtitle=subtitle,
                    participation_points=activity.points_participation,
                    winner_points=activity.points_win,
                    is_joined=is_joined,
                )
            )

            category.tasks_count += 1
            if is_joined:
                category.completed_count += 1

        return list(grouped.values())

    def get_categories(self, user_id: int) -> list[ActivityCategoryView]:
        return self._build_catalog(user_id)

    def get_category(self, user_id: int, slug: str) -> ActivityCategoryView | None:
        for category in self._build_catalog(user_id):
            if category.slug == slug and category.is_clickable:
                return category
        return None