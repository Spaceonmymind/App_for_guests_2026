from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return UserRepository(db).get_by_id(user_id)


def require_auth(request: Request, db: Session):
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse(url="/", status_code=303)
    return user