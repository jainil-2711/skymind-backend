"""
Itinerary Service
=================
Business logic for itinerary CRUD.

create()    — validate legs, compute totals, store as JSONB
list_user() — return all itineraries for a user
get()       — retrieve one with ownership check
delete()    — remove with ownership check
_compute()  — attach calculated fields to a raw Itinerary object

Interview talking point:
  destinations is stored as JSONB — a PostgreSQL type that stores
  arbitrary JSON and makes it queryable. This means we can store
  flexible, schema-free leg structures without a separate legs table,
  while still being able to query inside the JSON in future
  (e.g. WHERE destinations @> '[{"origin_iata": "DXB"}]').
"""

from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.repositories import itinerary_repo
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.itinerary import ItineraryCreateRequest, ItineraryOut


def _compute(itinerary: Itinerary) -> dict:
    """
    Compute derived fields from the JSONB destinations array.
    Returns a dict suitable for constructing ItineraryOut.
    """
    legs = itinerary.destinations or []
    total_legs = len(legs)

    prices = [
        float(leg["estimated_price_usd"])
        for leg in legs
        if leg.get("estimated_price_usd") is not None
    ]
    total_estimated_price_usd = round(sum(prices), 2) if prices else None

    durations = [
        int(leg["duration_min"])
        for leg in legs
        if leg.get("duration_min") is not None
    ]
    total_duration_min = sum(durations) if durations else None

    return {
        "id": itinerary.id,
        "user_id": itinerary.user_id,
        "prompt": itinerary.prompt,
        "destinations": legs,
        "total_budget_usd": float(itinerary.total_budget_usd) if itinerary.total_budget_usd else None,
        "duration_days": itinerary.duration_days,
        "llm_model": itinerary.llm_model,
        "created_at": itinerary.created_at,
        "total_legs": total_legs,
        "total_estimated_price_usd": total_estimated_price_usd,
        "total_duration_min": total_duration_min,
    }


def create(
    db: Session,
    user_id: UUID,
    payload: ItineraryCreateRequest,
) -> ItineraryOut:
    # Serialise legs to plain dicts for JSONB storage
    legs = [leg.model_dump() for leg in payload.destinations]

    itinerary = itinerary_repo.create(
        db,
        user_id=user_id,
        destinations=legs,
        prompt=payload.prompt,
        total_budget_usd=payload.total_budget_usd,
        duration_days=payload.duration_days,
        llm_model=None,     # Week 11 — Claude API wires this up
    )
    return ItineraryOut(**_compute(itinerary))


def list_user(db: Session, user_id: UUID) -> List[ItineraryOut]:
    itineraries = itinerary_repo.list_for_user(db, user_id)
    return [ItineraryOut(**_compute(i)) for i in itineraries]


def get(db: Session, itinerary_id: UUID, user_id: UUID) -> ItineraryOut:
    itinerary = itinerary_repo.get_by_id(db, itinerary_id)
    if not itinerary:
        raise NotFoundException("Itinerary not found")
    if itinerary.user_id != user_id:
        raise ForbiddenException("You do not own this itinerary")
    return ItineraryOut(**_compute(itinerary))


def delete(db: Session, itinerary_id: UUID, user_id: UUID) -> None:
    itinerary = itinerary_repo.get_by_id(db, itinerary_id)
    if not itinerary:
        raise NotFoundException("Itinerary not found")
    if itinerary.user_id != user_id:
        raise ForbiddenException("You do not own this itinerary")
    itinerary_repo.delete(db, itinerary)