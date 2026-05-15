from fastapi import APIRouter
from app.api.v1 import auth, users, flights

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(flights.router)