from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import require_auth
from app.repositories.fin_game_vote_repository import FinGameVoteRepository
from app.services.fin_game_voting_service import FinGameVotingError, FinGameVotingService

router = APIRouter(tags=["fin_game_voting"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/fin-game-voting", response_class=HTMLResponse)
def fin_game_voting_page(request: Request, db: Session = Depends(get_db)):
    current_user = require_auth(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    service = FinGameVotingService(db)
    games = service.get_games_for_user(user_id=current_user.id)
    existing_vote = FinGameVoteRepository(db).get_user_vote(user_id=current_user.id)

    vote_success = request.session.pop("fin_game_vote_success", False)
    vote_error = request.session.pop("fin_game_vote_error", None)

    return templates.TemplateResponse(
        request=request,
        name="participant/fin_game_voting.html",
        context={
            "title": "Голосование за лучшую фин-игру",
            "games": games,
            "existing_vote": existing_vote,
            "vote_success": vote_success,
            "vote_error": vote_error,
            "active_tab": "activities",
        },
    )


@router.post("/fin-game-voting", response_class=HTMLResponse)
async def fin_game_voting_submit(request: Request, db: Session = Depends(get_db)):
    current_user = require_auth(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    form = await request.form()
    activity_id_raw = str(form.get("activity_id", "")).strip()

    if not activity_id_raw.isdigit():
        request.session["fin_game_vote_error"] = "Выберите фин-игру для голосования."
        return RedirectResponse(url="/fin-game-voting", status_code=status.HTTP_303_SEE_OTHER)

    try:
        FinGameVotingService(db).submit_vote(
            user_id=current_user.id,
            activity_id=int(activity_id_raw),
        )
        request.session["fin_game_vote_success"] = True
    except FinGameVotingError as exc:
        request.session["fin_game_vote_error"] = str(exc)

    return RedirectResponse(url="/fin-game-voting", status_code=status.HTTP_303_SEE_OTHER)