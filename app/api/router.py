from fastapi import APIRouter

from app.api.v1 import auth, home, moderator, rating, activities, program,map, voting, master_poll

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(home.router)
api_router.include_router(moderator.router)
api_router.include_router(rating.router)
api_router.include_router(activities.router)
api_router.include_router(program.router)
api_router.include_router(map.router)
api_router.include_router(voting.router)
api_router.include_router(master_poll.router)