from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.user_repository import UserRepository
from app.services.master_poll_service import MasterPollError, MasterPollService
from app.core.security import require_auth
router = APIRouter(tags=["master_poll"])

templates = Jinja2Templates(directory="app/templates")


POLL_STEPS = [
    {
        "slug": "innovations",
        "title": "Инновации",
        "question": "Насколько вам легко даётся что-то новое, изменение привычного?",
        "answers": [
            "А) меня захватывает всё новое, я стремлюсь изучить это даже, если сначала освоить это кажется сложным",
            "Б) если инновация понятна для меня и легко доступна, то я ей воспользуюсь, в ином случае быстро потеряю интерес",
            "В) я очень избирательно отношусь к инновациям, предпочитаю сначала посмотреть как они используются другими, отзывы о них, обзоры по опыту их применения",
        ],
    },
    {
        "slug": "digital-currency",
        "title": "Цифровые валюты\nи токенизация",
        "question": "Насколько вы ощущаете свою готовность к повсеместному использованию цифровых валют (цифрового рубля, криптовалют) и цифровых финансовых активов?",
        "answers": [
            "А) С нетерпением жду понятных законных возможностей рассчитываться цифровыми валютами и понимаю суть цифровых активов",
            "Б) Не буду спешить, по мере необходимости буду осваивать и пользоваться цифровыми валютами и цифровыми активами",
            "В) Пока скорее мне непонятны возможности и безопасность этих видов финансовых инструментов",
        ],
    },
    {
        "slug": "ai-agents",
        "title": "Искусственный интеллект\nи межагентные платежи",
        "question": "Вы готовы доверить ИИ-агенту самостоятельно тратить ваши деньги (например, до 5000 рублей в месяц без вашего подтверждения)?",
        "answers": [
            "А) Да, это выглядит очень футуристично и сэкономит моё время",
            "Б) Если только на очень ограниченных сценариях (например, оплата подписок или парковки)",
            "В) Нет, я предпочту пока самостоятельно контролировать каждую транзакцию",
        ],
    },
    {
        "slug": "hyperpersonalization",
        "title": "Гиперперсонализация",
        "question": "Вы готовы делиться своими транзакционными данными с банком или маркетплейсом, если взамен получите действительно выгодные и точные предложения?",
        "answers": [
            "А) Да, если мне это экономит деньги или время",
            "Б) Только на обезличенной основе, чтобы меня нельзя было идентифицировать, а просто сделать вывод банку или маркетплейсу как улучшить продукты для потребителя",
            "В) Нет, финансовые данные — это слишком личное",
        ],
    },
]


def _get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    current_user = UserRepository(db).get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return None

    return current_user


@router.get("/master-poll", response_class=HTMLResponse)
def master_poll_start(request: Request, db: Session = Depends(get_db)):
    current_user = require_auth(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    service = MasterPollService(db)
    if service.is_completed(user_id=current_user.id):
        request.session["master_poll_error"] = "Вы уже прошли мастер-опрос."
        return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    request.session["master_poll_answers"] = {}

    first_step = POLL_STEPS[0]

    return templates.TemplateResponse(
        request=request,
        name="participant/master_poll_start.html",
        context={
            "title": "Мастер-опрос",
            "step_title": first_step["title"],
            "step_index": 1,
            "active_tab": "activities",
        },
    )


@router.get("/master-poll/result", response_class=HTMLResponse)
def master_poll_result(request: Request, db: Session = Depends(get_db)):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    finished = request.session.pop("master_poll_finished", False)
    if not finished:
        return RedirectResponse(url="/master-poll", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="participant/master_poll_result.html",
        context={
            "title": "Мастер-опрос",
            "active_tab": "activities",
        },
    )


@router.get("/master-poll/topic/{step_index}", response_class=HTMLResponse)
def master_poll_topic(step_index: int, request: Request, db: Session = Depends(get_db)):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    service = MasterPollService(db)
    if service.is_completed(user_id=current_user.id):
        request.session["master_poll_error"] = "Вы уже прошли мастер-опрос."
        return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    if step_index < 1 or step_index > len(POLL_STEPS):
        return RedirectResponse(url="/master-poll", status_code=status.HTTP_303_SEE_OTHER)

    step = POLL_STEPS[step_index - 1]

    return templates.TemplateResponse(
        request=request,
        name="participant/master_poll_start.html",
        context={
            "title": "Мастер-опрос",
            "step_title": step["title"],
            "step_index": step_index,
            "active_tab": "activities",
        },
    )


@router.get("/master-poll/{step_index}", response_class=HTMLResponse)
def master_poll_step(step_index: int, request: Request, db: Session = Depends(get_db)):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    service = MasterPollService(db)
    if service.is_completed(user_id=current_user.id):
        request.session["master_poll_error"] = "Вы уже прошли мастер-опрос."
        return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    if step_index < 1 or step_index > len(POLL_STEPS):
        return RedirectResponse(url="/master-poll", status_code=status.HTTP_303_SEE_OTHER)

    step = POLL_STEPS[step_index - 1]
    is_last = step_index == len(POLL_STEPS)

    return templates.TemplateResponse(
        request=request,
        name="participant/master_poll_question.html",
        context={
            "title": "Мастер-опрос",
            "step_index": step_index,
            "step_title": step["title"],
            "question": step["question"],
            "answers": step["answers"],
            "is_last": is_last,
            "active_tab": "activities",
        },
    )


@router.post("/master-poll/{step_index}", response_class=HTMLResponse)
def master_poll_submit_step(
    step_index: int,
    request: Request,
    answer: str = Form(...),
    db: Session = Depends(get_db),
):
    current_user = _get_current_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    service = MasterPollService(db)
    if service.is_completed(user_id=current_user.id):
        request.session["master_poll_error"] = "Вы уже прошли мастер-опрос."
        return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    if step_index < 1 or step_index > len(POLL_STEPS):
        return RedirectResponse(url="/master-poll", status_code=status.HTTP_303_SEE_OTHER)

    answers = request.session.get("master_poll_answers", {})
    answers[str(step_index)] = answer
    request.session["master_poll_answers"] = answers

    if step_index == len(POLL_STEPS):
        try:
            service.submit(user_id=current_user.id, answers=answers)
            request.session.pop("master_poll_answers", None)
            request.session["master_poll_finished"] = True
            return RedirectResponse(url="/master-poll/result", status_code=status.HTTP_303_SEE_OTHER)
        except MasterPollError as exc:
            request.session["master_poll_error"] = str(exc)
            return RedirectResponse(url="/activities", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url=f"/master-poll/topic/{step_index + 1}", status_code=status.HTTP_303_SEE_OTHER)