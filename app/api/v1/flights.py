from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import flight_service
from app.schemas.flight import FlightSearchRequest
from app.schemas.common import ApiResponse
from app.repositories import user_repo

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.post("/search", response_model=ApiResponse)
def search_flights(
    payload: FlightSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for flights between two airports.

    - Requires authentication (Bearer token)
    - Results are scored by price (40%), duration (35%), stops (25%)
    - Identical searches within 10 minutes are served from Redis cache
    - meta.cache_hit tells you whether this was a cache hit or miss
    """
    result = flight_service.search(
        origin=payload.origin,
        destination=payload.destination,
        departure_date=str(payload.departure_date),
        passengers=payload.passengers,
        cabin_class=payload.cabin_class,
    )
    return ApiResponse.ok(data=result["offers"], meta=result["meta"])