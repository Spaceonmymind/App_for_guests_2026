from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.rating_winner import RatingWinner


class RatingWinnerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def delete_all(self) -> None:
        self.db.execute(delete(RatingWinner))
        self.db.commit()

    def create(self, *, user_id: int, place: int) -> RatingWinner:
        winner = RatingWinner(user_id=user_id, place=place)
        self.db.add(winner)
        self.db.commit()
        self.db.refresh(winner)
        return winner

    def get_all(self) -> list[RatingWinner]:
        stmt = select(RatingWinner).order_by(RatingWinner.place.asc())
        return list(self.db.scalars(stmt).all())

    def get_winner_user_ids(self) -> set[int]:
        stmt = select(RatingWinner.user_id)
        return set(self.db.scalars(stmt).all())