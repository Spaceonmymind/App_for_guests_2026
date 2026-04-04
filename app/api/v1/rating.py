from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.rating_repository import RatingRepository
from app.repositories.rating_settings_repository import RatingSettingsRepository
from app.repositories.rating_winner_repository import RatingWinnerRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(tags=["rating"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/rating", response_class=HTMLResponse)
def rating_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    user_repo = UserRepository(db)
    current_user = user_repo.get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    leaderboard = RatingRepository(db).get_leaderboard()

    settings_repo = RatingSettingsRepository(db)
    winner_repo = RatingWinnerRepository(db)

    settings = settings_repo.get_or_create()
    winner_user_ids = winner_repo.get_winner_user_ids() if settings.is_finalized else set()

    current_user_place = None
    current_user_is_winner = False

    for item in leaderboard:
        item["show_gift"] = settings.is_finalized and item["user_id"] in winner_user_ids
        item["is_current_user"] = item["user_id"] == current_user.id

        if item["user_id"] == current_user.id:
            current_user_place = item["place"]
            current_user_is_winner = item["show_gift"]

    return templates.TemplateResponse(
        request=request,
        name="participant/rating.html",
        context={
            "title": "Рейтинг",
            "leaderboard": leaderboard,
            "current_user": {
                "id": current_user.id,
                "first_name": current_user.first_name or "",
                "last_name": current_user.last_name or "",
                "code": current_user.code,
            },
            "current_user_place": current_user_place,
            "current_user_is_winner": current_user_is_winner,
            "rating_is_finalized": settings.is_finalized,
            "active_tab": "rating",
        },
    )