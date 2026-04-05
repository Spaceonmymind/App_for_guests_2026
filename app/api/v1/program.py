from collections import OrderedDict
from datetime import date

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.program_repository import ProgramRepository
from app.repositories.user_repository import UserRepository
from app.core.security import require_auth
router = APIRouter(tags=["program"])

templates = Jinja2Templates(directory="app/templates")


def format_date_label(value: date) -> str:
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }
    return f"{value.day} {months[value.month]}"


@router.get("/program", response_class=HTMLResponse)
def program_page(
    request: Request,
    db: Session = Depends(get_db),
    selected_date: str | None = Query(default=None, alias="date"),
    hall: str | None = Query(default=None),
):
    current_user = require_auth(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    current_user = UserRepository(db).get_by_id(user_id)
    if current_user is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    repo = ProgramRepository(db)

    dates = repo.get_available_dates()
    halls = repo.get_available_halls()

    if not dates or not halls:
        return templates.TemplateResponse(
            request=request,
            name="participant/program.html",
            context={
                "title": "Программа",
                "date_tabs": [],
                "hall_tabs": [],
                "sessions": [],
                "session_groups": [],
                "current_date": None,
                "current_hall": None,
                "active_tab": "program",
            },
        )

    current_date = date.fromisoformat(selected_date) if selected_date else dates[0]
    if current_date not in dates:
        current_date = dates[0]

    hall_codes = {item["code"] for item in halls}
    current_hall = hall if hall in hall_codes else halls[0]["code"]

    sessions = repo.get_sessions(session_date=current_date, hall_code=current_hall)

    grouped_sections = OrderedDict()
    if current_hall == "brand-zone":
        for item in sessions:
            key = item.section_title or "Общая программа"
            grouped_sections.setdefault(key, []).append(item)

    date_tabs = [
        {
            "value": value.isoformat(),
            "label": format_date_label(value),
            "is_active": value == current_date,
        }
        for value in dates
    ]

    hall_tabs = [
        {
            "code": item["code"],
            "name": item["name"],
            "is_active": item["code"] == current_hall,
        }
        for item in halls
    ]

    session_groups = [
        {"title": title, "items": items}
        for title, items in grouped_sections.items()
    ]

    return templates.TemplateResponse(
        request=request,
        name="participant/program.html",
        context={
            "title": "Программа",
            "date_tabs": date_tabs,
            "hall_tabs": hall_tabs,
            "sessions": sessions,
            "session_groups": session_groups,
            "current_date": current_date.isoformat(),
            "current_hall": current_hall,
            "active_tab": "program",
        },
    )