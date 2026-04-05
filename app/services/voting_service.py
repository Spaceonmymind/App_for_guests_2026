from sqlalchemy.orm import Session

from app.repositories.vote_repository import VoteRepository
from app.repositories.voting_project_repository import VotingProjectRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_activity_repository import UserActivityRepository

class VotingError(Exception):
    pass


class VotingService:
    VOTING_ACTIVITY_NAME = "Голосование за лучший проект"
    VOTING_POINTS = 10
    VOTING_AWARD_TYPE = "best_project_vote"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vote_repo = VoteRepository(db)
        self.project_repo = VotingProjectRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.user_activity_repo = UserActivityRepository(db)

    def submit_vote(self, *, user_id: int, project_id: int) -> None:
        existing_vote = self.vote_repo.get_user_vote(user_id=user_id)
        if existing_vote is not None:
            raise VotingError("Вы уже проголосовали.")

        project = self.project_repo.get_by_id(project_id)
        if project is None or not project.is_active:
            raise VotingError("Проект для голосования не найден.")

        activity = self.activity_repo.get_by_name(self.VOTING_ACTIVITY_NAME)
        if activity is None:
            raise VotingError("Активность 'Голосование за лучший проект' не найдена в базе.")

        existing_award = self.user_activity_repo.get_existing_award(
            user_id=user_id,
            activity_id=activity.id,
            award_type=self.VOTING_AWARD_TYPE,
        )
        if existing_award is not None:
            raise VotingError("Баллы за голосование уже начислены.")

        self.vote_repo.create(user_id=user_id, project_id=project_id)

        self.user_activity_repo.create(
            user_id=user_id,
            activity_id=activity.id,
            award_type=self.VOTING_AWARD_TYPE,
            points=self.VOTING_POINTS,
            awarded_by_user_id=user_id,
        )