from fastapi import APIRouter, Depends, Request, status, FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.activity import Activity
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.admin_manual_award_rules import get_admin_award_options
from app.services.admin_manual_award_service import AdminManualAwardError, AdminManualAwardService
from app.repositories.master_poll_response_repository import MasterPollResponseRepository
from app.services.master_poll_results_service import MasterPollResultsService
from app.repositories.vote_repository import VoteRepository
from app.repositories.rating_winner_repository import RatingWinnerRepository
from app.repositories.rating_repository import RatingRepository
from app.services.rating_finalize_service import RatingFinalizeError, RatingFinalizeService
from app.repositories.moderator_activity_repository import ModeratorActivityRepository
from app.services.admin_score_code_service import AdminScoreCodeError, AdminScoreCodeService
from app.repositories.fin_game_vote_repository import FinGameVoteRepository

router = APIRouter(tags=["admin"])

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


def _require_admin(request: Request, db: Session):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return None

    if current_user.role != UserRole.ADMIN.value:
        return None

    return current_user


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="admin/home.html",
        context={
            "title": "Админка",
        },
    )


@router.get("/admin/moderators", response_class=HTMLResponse)
def admin_moderators(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    moderators = list(
        db.scalars(
            select(User)
            .where(User.role == UserRole.MODERATOR.value)
            .order_by(User.last_name.asc(), User.first_name.asc(), User.id.asc())
        ).all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/moderators.html",
        context={
            "title": "Модераторы",
            "moderators": moderators,
        },
    )


@router.get("/admin/activities", response_class=HTMLResponse)
def admin_activities(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    activities = list(
        db.scalars(
            select(Activity).order_by(Activity.name.asc(), Activity.id.asc())
        ).all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/activities.html",
        context={
            "title": "Активности",
            "activities": activities,
        },
    )

@router.get("/admin/moderator-activities", response_class=HTMLResponse)
def admin_moderator_activities(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    moderators = list(
        db.scalars(
            select(User)
            .where(User.role == UserRole.MODERATOR.value)
            .order_by(User.last_name.asc(), User.first_name.asc(), User.id.asc())
        ).all()
    )

    activities = list(
        db.scalars(
            select(Activity).order_by(Activity.name.asc(), Activity.id.asc())
        ).all()
    )

    bindings = ModeratorActivityRepository(db).get_all_bindings()

    success_message = request.session.pop("admin_success_message", None)
    error_message = request.session.pop("admin_error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="admin/moderator_activities.html",
        context={
            "title": "Привязка активностей",
            "moderators": moderators,
            "activities": activities,
            "bindings": bindings,
            "success_message": success_message,
            "error_message": error_message,
        },
    )


@router.post("/admin/moderator-activities", response_class=HTMLResponse)
def admin_create_moderator_activity(
    request: Request,
    db: Session = Depends(get_db),
    moderator_user_id: int = Form(...),
    activity_id: int = Form(...),
):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    moderator = db.get(User, moderator_user_id)
    if moderator is None or moderator.role != UserRole.MODERATOR.value:
        request.session["admin_error_message"] = "Выбранный пользователь не является модератором."
        return RedirectResponse(url="/admin/moderator-activities", status_code=status.HTTP_303_SEE_OTHER)

    activity = db.get(Activity, activity_id)
    if activity is None:
        request.session["admin_error_message"] = "Выбранная активность не найдена."
        return RedirectResponse(url="/admin/moderator-activities", status_code=status.HTTP_303_SEE_OTHER)

    repo = ModeratorActivityRepository(db)
    existing = repo.get_existing(
        moderator_user_id=moderator_user_id,
        activity_id=activity_id,
    )
    if existing is not None:
        request.session["admin_error_message"] = "Такая привязка уже существует."
        return RedirectResponse(url="/admin/moderator-activities", status_code=status.HTTP_303_SEE_OTHER)

    repo.create(
        moderator_user_id=moderator_user_id,
        activity_id=activity_id,
    )
    request.session["admin_success_message"] = "Привязка успешно создана."
    return RedirectResponse(url="/admin/moderator-activities", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/moderator-activities/{binding_id}/delete", response_class=HTMLResponse)
def admin_delete_moderator_activity(
    binding_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    deleted = ModeratorActivityRepository(db).delete_by_id(binding_id)
    if deleted:
        request.session["admin_success_message"] = "Привязка удалена."
    else:
        request.session["admin_error_message"] = "Привязка не найдена."

    return RedirectResponse(url="/admin/moderator-activities", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/admin/manual-awards", response_class=HTMLResponse)
def admin_manual_awards(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    activities = list(
        db.scalars(
            select(Activity).order_by(Activity.name.asc(), Activity.id.asc())
        ).all()
    )

    selected_activity_id = request.query_params.get("activity_id")
    selected_activity = None
    award_options = []

    if selected_activity_id and str(selected_activity_id).isdigit():
        selected_activity = db.get(Activity, int(selected_activity_id))
        if selected_activity is not None:
            award_options = get_admin_award_options(selected_activity.name)

    success_message = request.session.pop("admin_success_message", None)
    error_message = request.session.pop("admin_error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="admin/manual_awards.html",
        context={
            "title": "Начислить / отнять баллы",
            "activities": activities,
            "selected_activity": selected_activity,
            "award_options": award_options,
            "success_message": success_message,
            "error_message": error_message,
        },
    )


@router.post("/admin/manual-awards", response_class=HTMLResponse)
def admin_apply_manual_award(
    request: Request,
    db: Session = Depends(get_db),
    participant_code: str = Form(...),
    activity_id: int = Form(...),
    award_type: str = Form(...),
    operation: str = Form(...),
):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        points = AdminManualAwardService(db).apply(
            admin_user_id=current_user.id,
            participant_code=participant_code.strip(),
            activity_id=activity_id,
            award_type=award_type,
            operation=operation,
        )
        request.session["admin_success_message"] = (
            f"Операция выполнена. Изменение баллов: {points}."
        )
    except AdminManualAwardError as exc:
        request.session["admin_error_message"] = str(exc)

    return RedirectResponse(
        url=f"/admin/manual-awards?activity_id={activity_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )

@router.get("/admin/master-poll-results", response_class=HTMLResponse)
def admin_master_poll_results(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    response_repo = MasterPollResponseRepository(db)
    results = MasterPollResultsService(response_repo).build_results()

    return templates.TemplateResponse(
        request=request,
        name="admin/master_poll_results.html",
        context={
            "title": "Результаты мастер-опроса",
            "results": results,
        },
    )

@router.get("/admin/voting-results", response_class=HTMLResponse)
def admin_voting_results(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    results = VoteRepository(db).get_results()

    return templates.TemplateResponse(
        request=request,
        name="admin/voting_results.html",
        context={
            "title": "Результаты голосования",
            "results": results,
        },
    )

@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    users = list(
        db.scalars(
            select(User).order_by(User.role.asc(), User.last_name.asc(), User.first_name.asc(), User.id.asc())
        ).all()
    )

    success_message = request.session.pop("admin_success_message", None)
    error_message = request.session.pop("admin_error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={
            "title": "Пользователи",
            "users": users,
            "success_message": success_message,
            "error_message": error_message,
        },
    )

@router.get("/admin/rating-finalize", response_class=HTMLResponse)
def admin_rating_finalize_page(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    leaderboard = RatingRepository(db).get_leaderboard()
    preview_top = leaderboard[:15]
    winner_rows = RatingWinnerRepository(db).get_all()

    winners = []
    for item in winner_rows:
        user = db.get(User, item.user_id)
        if user:
            winners.append({
                "place": item.place,
                "code": user.code,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })

    success_message = request.session.pop("admin_success_message", None)
    error_message = request.session.pop("admin_error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="admin/rating_finalize.html",
        context={
            "title": "Завершение рейтинга",
            "preview_top": preview_top,
            "winners": winners,
            "success_message": success_message,
            "error_message": error_message,
        },
    )


@router.post("/admin/rating-finalize", response_class=HTMLResponse)
def admin_rating_finalize(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        created = RatingFinalizeService(db).finalize(admin_user_id=current_user.id)
        request.session["admin_success_message"] = f"Рейтинг завершен. Сформировано победителей: {created}."
    except RatingFinalizeError as exc:
        request.session["admin_error_message"] = str(exc)

    return RedirectResponse(url="/admin/rating-finalize", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/users/{user_id}/regenerate-score-code", response_class=HTMLResponse)
def admin_regenerate_score_code(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    try:
        new_code = AdminScoreCodeService(db).regenerate(user_id=user_id)
        request.session["admin_success_message"] = f"Новый короткий код создан: {new_code}"
    except AdminScoreCodeError as exc:
        request.session["admin_error_message"] = str(exc)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/admin/fin-game-voting-results", response_class=HTMLResponse)
def admin_fin_game_voting_results(request: Request, db: Session = Depends(get_db)):
    current_user = _require_admin(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    results = FinGameVoteRepository(db).get_results()

    return templates.TemplateResponse(
        request=request,
        name="admin/fin_game_voting_results.html",
        context={
            "title": "Результаты голосования за лучшую фин-игру",
            "results": results,
        },
    )