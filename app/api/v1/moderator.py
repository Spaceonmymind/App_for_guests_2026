from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import UserRole
from app.repositories.moderator_activity_repository import ModeratorActivityRepository
from app.repositories.user_repository import UserRepository
from app.services.moderator_activity_rules import get_award_options
from app.services.moderator_award_service import ModeratorAwardError, ModeratorAwardService

router = APIRouter(tags=["moderator"])

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


@router.get("/moderator", response_class=HTMLResponse)
def moderator_page(
    request: Request,
    db: Session = Depends(get_db),
    activity_id: int | None = Query(default=None),
):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if current_user.role not in {UserRole.MODERATOR.value, UserRole.ADMIN.value}:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    moderator_activity_repo = ModeratorActivityRepository(db)
    available_activities = moderator_activity_repo.get_activities_for_moderator(
        moderator_user_id=current_user.id
    )

    if not available_activities:
        return templates.TemplateResponse(
            request=request,
            name="moderator/score.html",
            context={
                "title": "Модератор",
                "activities": [],
                "selected_activity": None,
                "award_options": [],
                "error_message": "За вами пока не закреплены активности.",
                "success_message": None,
            },
        )

    selected_activity = None

    if activity_id is not None:
        for activity in available_activities:
            if activity.id == activity_id:
                selected_activity = activity
                break

    if selected_activity is None:
        selected_activity = available_activities[0]

    award_options = get_award_options(selected_activity.name)

    success_message = request.session.pop("moderator_success_message", None)
    error_message = request.session.pop("moderator_error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="moderator/score.html",
        context={
            "title": "Модератор",
            "activities": available_activities,
            "selected_activity": selected_activity,
            "award_options": award_options,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@router.post("/moderator/award", response_class=HTMLResponse)
def moderator_award(
    request: Request,
    db: Session = Depends(get_db),
    activity_id: int = Form(...),
    participant_code: str = Form(...),
    award_type: str = Form(...),
):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if current_user.role not in {UserRole.MODERATOR.value, UserRole.ADMIN.value}:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        ModeratorAwardService(db).award(
            moderator_user_id=current_user.id,
            participant_code=participant_code.strip(),
            activity_id=activity_id,
            award_type=award_type,
        )
        request.session["moderator_success_message"] = f"Код {participant_code.strip()} — баллы начислены."
    except ModeratorAwardError as exc:
        request.session["moderator_error_message"] = str(exc)

    return RedirectResponse(
        url=f"/moderator?activity_id={activity_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )