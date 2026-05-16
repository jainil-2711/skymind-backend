"""
Saved Search Service
====================
Business logic for saved searches.

create()  — save a search config for a user
list()    — return all saved searches for a user
get()     — retrieve one saved search (with ownership check)
rerun()   — retrieve one saved search and re-run it live
delete()  — remove a saved search (ownership check)

Interview talking point:
  rerun() is the most interesting function here. It takes a stored
  search configuration and calls flight_service.search() with it —
  the same pipeline used by the live search endpoint. The user gets
  fresh live results from their saved config with one API call.
"""

from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.saved_search import SavedSearch
from app.repositories import saved_search_repo
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.saved_search import SavedSearchCreateRequest


def create(
    db: Session,
    user_id: UUID,
    payload: SavedSearchCreateRequest,
) -> SavedSearch:
    return saved_search_repo.create(
        db,
        user_id=user_id,
        origin_iata=payload.origin,
        destination_iata=payload.destination,
        depart_date=payload.depart_date,
        return_date=payload.return_date,
        passengers=payload.passengers,
        cabin_class=payload.cabin_class,
    )


def list_user(db: Session, user_id: UUID) -> List[SavedSearch]:
    return saved_search_repo.list_for_user(db, user_id)


def get(db: Session, saved_search_id: UUID, user_id: UUID) -> SavedSearch:
    saved = saved_search_repo.get_by_id(db, saved_search_id)
    if not saved:
        raise NotFoundException("Saved search not found")
    if saved.user_id != user_id:
        raise ForbiddenException("You do not own this saved search")
    return saved


def rerun(db: Session, saved_search_id: UUID, user_id: UUID) -> dict:
    """
    Retrieve a saved search and re-execute it against the live flight pipeline.
    Returns the scored flight offers exactly as POST /flights/search would.
    """
    from app.services.flight_service import search as flight_search

    saved = get(db, saved_search_id, user_id)

    result = flight_search(
        origin=saved.origin_iata,
        destination=saved.destination_iata,
        departure_date=str(saved.depart_date),
        passengers=saved.passengers,
        cabin_class=saved.cabin_class,
        user_id=user_id,
        db=db,
    )
    return {
        "saved_search": saved,
        "result": result,
    }


def delete(db: Session, saved_search_id: UUID, user_id: UUID) -> None:
    saved = saved_search_repo.get_by_id(db, saved_search_id)
    if not saved:
        raise NotFoundException("Saved search not found")
    if saved.user_id != user_id:
        raise ForbiddenException("You do not own this saved search")
    saved_search_repo.delete(db, saved)