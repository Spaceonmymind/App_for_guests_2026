from sqlalchemy.orm import Session

from app.repositories.activity_repository import ActivityRepository
from app.repositories.fin_game_vote_repository import FinGameVoteRepository
from app.repositories.user_activity_repository import UserActivityRepository


class FinGameVotingError(Exception):
    pass


class FinGameVotingService:
    FIN_GAME_VOTE_ACTIVITY_NAME = "Голосование за лучшую фин-игру"
    FIN_GAME_VOTE_POINTS = 10
    FIN_GAME_VOTE_AWARD_TYPE = "best_fin_game_vote"

    FIN_GAME_NAMES = {
        "Юный инвестор",
        "Инновационный ширпотреб",
        "Финансовый детектив",
        "Накопи на мечту",
        "Мамин инвестор",
        "Жажда власти",
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vote_repo = FinGameVoteRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def get_games_for_user(self, *, user_id: int) -> list[dict]:
        all_activities = self.activity_repo.get_all()
        joined_ids = set(
            self.user_activity_repo.get_awarded_activity_ids_for_user(user_id=user_id)
        )

        result = []
        for activity in all_activities:
            if activity.name not in self.FIN_GAME_NAMES:
                continue

            result.append(
                {
                    "id": activity.id,
                    "name": activity.name,
                    "is_available": activity.id in joined_ids,
                }
            )

        return result

    def has_voted(self, *, user_id: int) -> bool:
        return self.vote_repo.get_user_vote(user_id=user_id) is not None

    def submit_vote(self, *, user_id: int, activity_id: int) -> None:
        existing_vote = self.vote_repo.get_user_vote(user_id=user_id)
        if existing_vote is not None:
            raise FinGameVotingError("Вы уже проголосовали за лучшую фин-игру.")

        games = self.get_games_for_user(user_id=user_id)
        allowed_ids = {item["id"] for item in games if item["is_available"]}

        if activity_id not in allowed_ids:
            raise FinGameVotingError("Голосовать можно только за ту фин-игру, в которой вы участвовали.")

        voting_activity = self.activity_repo.get_by_name(self.FIN_GAME_VOTE_ACTIVITY_NAME)
        if voting_activity is None:
            raise FinGameVotingError("Активность 'Голосование за лучшую фин-игру' не найдена.")

        existing_award = self.user_activity_repo.get_existing_award(
            user_id=user_id,
            activity_id=voting_activity.id,
            award_type=self.FIN_GAME_VOTE_AWARD_TYPE,
        )
        if existing_award is not None:
            raise FinGameVotingError("Баллы за голосование уже начислены.")

        self.vote_repo.create(user_id=user_id, activity_id=activity_id)

        self.user_activity_repo.create(
            user_id=user_id,
            activity_id=voting_activity.id,
            award_type=self.FIN_GAME_VOTE_AWARD_TYPE,
            points=self.FIN_GAME_VOTE_POINTS,
            awarded_by_user_id=user_id,
        )