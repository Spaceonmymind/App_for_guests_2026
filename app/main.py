from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)