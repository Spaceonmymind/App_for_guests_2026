from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master_poll_response import MasterPollResponse
from app.models.vote import Vote
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository
from app.models.fin_game_vote import FinGameVote
from app.repositories.feature_flags_repository import FeatureFlagsRepository


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
    badge_mode: str
    is_completed: bool = False
    is_open: bool = True
    closed_text: str = ""


class ActivitiesCatalogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)
        self.feature_flags_repo = FeatureFlagsRepository(db)

    def _is_master_poll_completed(self, user_id: int) -> bool:
        return self.db.scalar(
            select(MasterPollResponse).where(MasterPollResponse.user_id == user_id)
        ) is not None

    def _is_best_project_vote_completed(self, user_id: int) -> bool:
        return self.db.scalar(
            select(Vote).where(Vote.user_id == user_id)
        ) is not None

    def _is_best_fin_game_vote_completed(self, user_id: int) -> bool:
        return self.db.scalar(
            select(FinGameVote).where(FinGameVote.user_id == user_id)
        ) is not None

    def _build_catalog(self, user_id: int) -> list[ActivityCategoryView]:
        activities = self.activity_repo.get_all()
        joined_ids = self.user_activity_repo.get_awarded_activity_ids_for_user(user_id=user_id)
        flags = self.feature_flags_repo.get_or_create()

        grouped["master-poll"].is_open = flags.is_master_poll_open
        grouped["master-poll"].closed_text = "Откроется в 10:30"

        grouped["best-project-vote"].is_open = flags.is_project_voting_open
        grouped["best-project-vote"].closed_text = "Откроется в  17:00"

        grouped: dict[str, ActivityCategoryView] = {
            "master-poll": ActivityCategoryView(
                slug="master-poll",
                title="Мастер-опрос",
                subtitle="Бренд-зона НСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=True,
                badge_mode="poll",
            ),
            "best-project-vote": ActivityCategoryView(
                slug="best-project-vote",
                title="Голосование\nза лучший проект",
                subtitle="",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=True,
                badge_mode="vote",
            ),
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
            "best-fin-game-vote": ActivityCategoryView(
                slug="best-fin-game-vote",
                title="Голосование за\nлучшую игру",
                subtitle="Зал финансовых игр",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=True,
                badge_mode="vote",
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
            "quiz": ActivityCategoryView(
                slug="quiz",
                title="Квиз Мир\nPlat.Form",
                subtitle="Бренд-зона НСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "resume-roast": ActivityCategoryView(
                slug="resume-roast",
                title="Прожарка\nрезюме",
                subtitle="Бренд-зона НСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "fintech-guru": ActivityCategoryView(
                slug="fintech-guru",
                title="Финтех-гуру",
                subtitle="Бренд-зона НСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
            "ideas-world": ActivityCategoryView(
                slug="ideas-world",
                title="Мир идей",
                subtitle="Бренд-зона НСПК",
                tasks_count=0,
                completed_count=0,
                tasks=[],
                is_clickable=False,
                badge_mode="standard",
            ),
        }

        grouped["master-poll"].is_completed = self._is_master_poll_completed(user_id)
        grouped["best-project-vote"].is_completed = self._is_best_project_vote_completed(user_id)
        grouped["best-fin-game-vote"].is_completed = self._is_best_fin_game_vote_completed(user_id)

        financial_map = {
            "Юный инвестор": "Игра «Юный инвестор»",
            "Инновационный ширпотреб": "Игра «Инновационный ширпотреб»",
            "Финансовый детектив": "Игра «Финансовый детектив»",
            "Накопи на мечту": "Игра «Накопи на мечту»",
            "Мамин инвестор": "Игра «Мамин инвестор»",
            "Жажда власти": "Игра «Жажда власти»",
        }

        constructor_map = {
            "ПС Мир": "ПС Мир",
            "СБП": "СБП",
            "Блокчейн": "Блокчейн",
            "3D-Secure": "3D-Secure",
        }

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
            elif activity.name == "Квиз Мир Plat.Form":
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

        for category in grouped.values():
            if category.badge_mode not in {"poll", "vote"}:
                category.is_completed = (
                    category.tasks_count > 0 and category.completed_count == category.tasks_count
                )

        return list(grouped.values())

    def get_category(self, user_id: int, slug: str) -> ActivityCategoryView | None:
        for category in self._build_catalog(user_id):
            if category.slug == slug and category.slug in {"financial-games", "transaction-constructor"}:
                return category
        return None

    def get_categories(self, user_id: int) -> list[ActivityCategoryView]:
        return self._build_catalog(user_id)

