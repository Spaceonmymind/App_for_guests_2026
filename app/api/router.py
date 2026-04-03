from fastapi import APIRouter

from app.api.v1 import auth, home, moderator, rating

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(home.router)
api_router.include_router(moderator.router)
api_router.include_router(rating.router)
