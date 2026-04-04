from sqlalchemy.orm import Session

from app.repositories.vote_repository import VoteRepository
from app.repositories.voting_project_repository import VotingProjectRepository


class VotingError(Exception):
    pass


class VotingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.vote_repo = VoteRepository(db)
        self.project_repo = VotingProjectRepository(db)

    def submit_vote(self, *, user_id: int, project_id: int) -> None:
        existing_vote = self.vote_repo.get_user_vote(user_id=user_id)
        if existing_vote is not None:
            raise VotingError("Вы уже проголосовали.")

        project = self.project_repo.get_by_id(project_id)
        if project is None or not project.is_active:
            raise VotingError("Проект для голосования не найден.")

        self.vote_repo.create(user_id=user_id, project_id=project_id)