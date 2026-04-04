from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import UserActivationStatus
from app.repositories.user_repository import UserRepository
from app.services.score_code_service import ScoreCodeService
from app.models.user import UserRole
router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "Вход",
            "error": None,
            "entered_code": "",
        },
    )


@router.post("/auth/login", response_class=HTMLResponse)
def login_by_code(
    request: Request,
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    normalized_code = code.strip().upper()

    if not (6 <= len(normalized_code) <= 9):
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Вход",
                "error": "Введите корректный код (6–9 символов).",
                "entered_code": normalized_code,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_code(normalized_code)

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Вход",
                "error": "Пользователь с таким кодом не найден.",
                "entered_code": normalized_code,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if user.activation_status == UserActivationStatus.PENDING.value:
        return RedirectResponse(
            url=f"/auth/activate?code={user.code}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if user.role == UserRole.PARTICIPANT.value and user.score_code is None:
        score_code = ScoreCodeService(user_repo).generate_unique()
        user.score_code = score_code
        db.commit()

    request.session["user_id"] = user.id

    if user.role == UserRole.MODERATOR.value:
        return RedirectResponse(
            url="/moderator",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if user.role == UserRole.ADMIN.value:
        return RedirectResponse(
            url="/admin",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url="/home",
        status_code=status.HTTP_303_SEE_OTHER,
    )

@router.get("/auth/activate", response_class=HTMLResponse)
def activate_page(
    request: Request,
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    normalized_code = code.strip().upper()
    user = user_repo.get_by_code(normalized_code)

    if user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if user.activation_status == UserActivationStatus.ACTIVE.value:
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="auth/activate.html",
        context={
            "title": "Активация профиля",
            "code": normalized_code,
            "error": None,
            "first_name": "",
            "last_name": "",
        },
    )


@router.post("/auth/activate", response_class=HTMLResponse)
def activate_user(
    request: Request,
    code: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    db: Session = Depends(get_db),
):
    normalized_code = code.strip().upper()
    normalized_first_name = first_name.strip()
    normalized_last_name = last_name.strip()

    user_repo = UserRepository(db)
    user = user_repo.get_by_code(normalized_code)

    if user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if not normalized_first_name or not normalized_last_name:
        return templates.TemplateResponse(
            request=request,
            name="auth/activate.html",
            context={
                "title": "Активация профиля",
                "code": normalized_code,
                "error": "Заполните имя и фамилию.",
                "first_name": normalized_first_name,
                "last_name": normalized_last_name,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    activated_user = user_repo.activate_user(
        user=user,
        first_name=normalized_first_name,
        last_name=normalized_last_name,
    )

    if (
        activated_user.role == UserRole.PARTICIPANT.value
        and activated_user.score_code is None
    ):
        score_code = ScoreCodeService(user_repo).generate_unique()
        activated_user.score_code = score_code
        db.commit()
        db.refresh(activated_user)

    request.session["user_id"] = activated_user.id

    return RedirectResponse(
        url="/home",
        status_code=status.HTTP_303_SEE_OTHER,
    )