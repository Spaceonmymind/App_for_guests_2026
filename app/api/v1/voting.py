from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.repositories.feature_flags_repository import FeatureFlagsRepository
from app.api.deps import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.vote_repository import VoteRepository
from app.repositories.voting_project_repository import VotingProjectRepository
from app.services.voting_service import VotingError, VotingService
from app.core.security import require_auth
router = APIRouter(tags=["voting"])

templates = Jinja2Templates(directory="app/templates")


def _get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    current_user = UserRepository(db).get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return None

    return current_user


@router.get("/voting", response_class=HTMLResponse)
def voting_page(request: Request, db: Session = Depends(get_db)):
    current_user = require_auth(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    flags = FeatureFlagsRepository(db).get_or_create()
    if not flags.is_project_voting_open:
        return RedirectResponse(url="/home?voting_closed=1", status_code=status.HTTP_303_SEE_OTHER)

    projects = VotingProjectRepository(db).get_active_projects()
    existing_vote = VoteRepository(db).get_user_vote(user_id=current_user.id)

    vote_success = request.session.pop("vote_success", False)
    vote_error = request.session.pop("vote_error", None)

    return templates.TemplateResponse(
        request=request,
        name="participant/voting.html",
        context={
            "title": "Голосование",
            "projects": projects,
            "existing_vote": existing_vote,
            "vote_success": vote_success,
            "vote_error": vote_error,
            "active_tab": "voting",
        },
    )

@router.post("/voting", response_class=HTMLResponse)
def submit_vote(
    request: Request,
    project_id: int = Form(...),
    db: Session = Depends(get_db),
):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        VotingService(db).submit_vote(user_id=current_user.id, project_id=project_id)
        request.session["vote_success"] = True
    except VotingError as exc:
        request.session["vote_error"] = str(exc)

    return RedirectResponse(url="/voting", status_code=status.HTTP_303_SEE_OTHER)