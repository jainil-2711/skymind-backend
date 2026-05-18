from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import flights
from app.api.v1 import routes
from app.api.v1 import alerts
from app.api.v1 import analytics
from app.api.v1 import saved_searches
from app.api.v1 import itineraries
from app.api.v1 import destinations
from app.api.v1 import planner

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(flights.router)
api_router.include_router(routes.router)
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
api_router.include_router(saved_searches.router)
api_router.include_router(itineraries.router)
api_router.include_router(destinations.router)
api_router.include_router(planner.router)