from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.services.score_code_service import ScoreCodeService

from app.core.security import require_auth

router = APIRouter(tags=["home"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    user = require_auth(request, db)
    if isinstance(user, RedirectResponse):
        return user

    user_repo = UserRepository(db)

    if user.role == UserRole.PARTICIPANT.value and user.score_code is None:
        score_code = ScoreCodeService(user_repo).generate_unique()
        user.score_code = score_code
        db.commit()
        db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="participant/home.html",
        context={
            "title": "Главное меню",
            "user": {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "role_label": "участник",
                "code": user.code,
                "score_code": user.score_code,
            },
            "menu_items": [
                {"title": "Карта", "icon": "/static/img/icon-map.png", "href": "/map"},
                {"title": "Программа", "icon": "/static/img/icon-program.png", "href": "/program"},
                {"title": "Интерактивы", "icon": "/static/img/icon-activities.png", "href": "/activities"},
                {"title": "Рейтинг", "icon": "/static/img/icon-rating.png", "href": "/rating"},
                {"title": "Голосование", "icon": "/static/img/icon-voting.png", "href": "/voting"},
            ],
            "voting_closed": request.query_params.get("voting_closed") == "1",
            "master_poll_closed": request.query_params.get("master_poll_closed") == "1",
        },
    )