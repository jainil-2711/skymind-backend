from fastapi import APIRouter
from app.api.v1 import auth, users, flights, routes, alerts, analytics

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(flights.router)
api_router.include_router(routes.router)
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)