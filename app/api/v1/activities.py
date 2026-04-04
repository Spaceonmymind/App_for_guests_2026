from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.user_repository import UserRepository
from app.services.activities_catalog_service import ActivitiesCatalogService

router = APIRouter(tags=["activities"])

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


@router.get("/activities", response_class=HTMLResponse)
def activities_page(request: Request, db: Session = Depends(get_db)):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    categories = ActivitiesCatalogService(db).get_categories(current_user.id)

    return templates.TemplateResponse(
        request=request,
        name="participant/activities.html",
        context={
            "title": "Интерактивы",
            "categories": categories,
            "active_tab": "activities",
        },
    )


@router.get("/activities/{slug}", response_class=HTMLResponse)
def activity_category_page(slug: str, request: Request, db: Session = Depends(get_db)):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    category = ActivitiesCatalogService(db).get_category(current_user.id, slug)
    if category is None:
        return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="participant/activity_category.html",
        context={
            "title": category.title,
            "category": category,
            "active_tab": "activities",
            "error": None,
            "success": None,
        },
    )