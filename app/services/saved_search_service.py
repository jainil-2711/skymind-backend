"""
Saved Search Service
====================
Fixed in Week 9: removed the cross-service import of flight_service.
rerun() no longer calls flight_service directly.
The router now handles orchestration between saved_search_service and flight_service,
keeping services independent as the blueprint requires.
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


def delete(db: Session, saved_search_id: UUID, user_id: UUID) -> None:
    saved = saved_search_repo.get_by_id(db, saved_search_id)
    if not saved:
        raise NotFoundException("Saved search not found")
    if saved.user_id != user_id:
        raise ForbiddenException("You do not own this saved search")
    saved_search_repo.delete(db, saved)