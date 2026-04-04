from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter(tags=["home"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

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
            },
            "menu_items": [
                {"title": "Карта", "icon": "/static/img/icon-map.png", "href": "/map"},
                {"title": "Программа", "icon": "/static/img/icon-program.png", "href": "/program"},
                {"title": "Интерактивы", "icon": "/static/img/icon-activities.png", "href": "/activities"},
                {"title": "Рейтинг", "icon": "/static/img/icon-rating.png", "href": "/rating"},
                {"title": "Голосование", "icon": "/static/img/icon-voting.png", "href": "/voting"},
            ],
        },
    )