from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import UserRole
from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository
from app.services.scoring_service import ScoringError, ScoringService

router = APIRouter(tags=["moderator"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/moderator/score", response_class=HTMLResponse)
def moderator_score_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    user_repo = UserRepository(db)
    current_user = user_repo.get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if current_user.role not in {UserRole.MODERATOR.value, UserRole.ADMIN.value}:
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

    activities = ActivityRepository(db).get_all()

    return templates.TemplateResponse(
        request=request,
        name="moderator/score.html",
        context={
            "title": "Начисление баллов",
            "activities": activities,
            "error": None,
            "success": None,
            "entered_code": "",
            "selected_activity_id": None,
            "selected_award_type": "participation",
        },
    )


@router.post("/moderator/score", response_class=HTMLResponse)
def moderator_score_submit(
    request: Request,
    participant_code: str = Form(...),
    activity_id: int = Form(...),
    award_type: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    user_repo = UserRepository(db)
    current_user = user_repo.get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    activities = ActivityRepository(db).get_all()
    scoring_service = ScoringService(db)

    try:
        scoring_service.award_points(
            participant_code=participant_code.strip(),
            activity_id=activity_id,
            award_type=award_type,
            moderator_user_id=current_user.id,
        )
    except ScoringError as exc:
        return templates.TemplateResponse(
            request=request,
            name="moderator/score.html",
            context={
                "title": "Начисление баллов",
                "activities": activities,
                "error": str(exc),
                "success": None,
                "entered_code": participant_code.strip(),
                "selected_activity_id": activity_id,
                "selected_award_type": award_type,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return templates.TemplateResponse(
        request=request,
        name="moderator/score.html",
        context={
            "title": "Начисление баллов",
            "activities": activities,
            "error": None,
            "success": "Баллы успешно начислены.",
            "entered_code": "",
            "selected_activity_id": activity_id,
            "selected_award_type": award_type,
        },
    )