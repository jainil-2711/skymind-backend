from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import itinerary_service
from app.schemas.itinerary import ItineraryCreateRequest, ItineraryOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/itineraries", tags=["Itineraries"])


@router.post("", response_model=ApiResponse, status_code=201)
def create_itinerary(
    payload: ItineraryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a multi-leg itinerary.
    Legs are stored as a JSONB array — flexible, queryable, schema-free.
    Computed fields (total_legs, total_estimated_price_usd, total_duration_min)
    are derived from the legs on every read.
    Week 11 will add LLM generation — prompt field used then.
    """
    itinerary = itinerary_service.create(db, user_id=current_user.id, payload=payload)
    return ApiResponse.ok(itinerary.model_dump())


@router.get("", response_model=ApiResponse)
def list_itineraries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all itineraries for the authenticated user. Most recent first."""
    itineraries = itinerary_service.list_user(db, user_id=current_user.id)
    return ApiResponse.ok([i.model_dump() for i in itineraries])


@router.get("/{itinerary_id}", response_model=ApiResponse)
def get_itinerary(
    itinerary_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve one itinerary with all legs and computed totals.
    Returns 404 if not found, 403 if not owner.
    """
    itinerary = itinerary_service.get(
        db, itinerary_id=itinerary_id, user_id=current_user.id
    )
    return ApiResponse.ok(itinerary.model_dump())


@router.delete("/{itinerary_id}", status_code=204)
def delete_itinerary(
    itinerary_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an itinerary. Only the owner can delete. Returns 204 No Content."""
    itinerary_service.delete(
        db, itinerary_id=itinerary_id, user_id=current_user.id
    )