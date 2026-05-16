from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.saved_search import SavedSearch


def create(
    db: Session,
    user_id: UUID,
    origin_iata: str,
    destination_iata: str,
    depart_date,
    return_date=None,
    passengers: int = 1,
    cabin_class: str = "ECONOMY",
) -> SavedSearch:
    row = SavedSearch(
        user_id=user_id,
        origin_iata=origin_iata,
        destination_iata=destination_iata,
        depart_date=depart_date,
        return_date=return_date,
        passengers=passengers,
        cabin_class=cabin_class,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_by_id(db: Session, saved_search_id: UUID) -> Optional[SavedSearch]:
    return db.query(SavedSearch).filter(SavedSearch.id == saved_search_id).first()


def list_for_user(db: Session, user_id: UUID) -> List[SavedSearch]:
    return (
        db.query(SavedSearch)
        .filter(SavedSearch.user_id == user_id)
        .order_by(desc(SavedSearch.created_at))
        .all()
    )


def delete(db: Session, saved_search: SavedSearch) -> None:
    db.delete(saved_search)
    db.commit()