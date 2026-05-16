from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.itinerary import Itinerary


def create(
    db: Session,
    user_id: UUID,
    destinations: list,
    prompt: Optional[str] = None,
    total_budget_usd: Optional[float] = None,
    duration_days: Optional[int] = None,
    llm_model: Optional[str] = None,
) -> Itinerary:
    row = Itinerary(
        user_id=user_id,
        prompt=prompt,
        destinations=destinations,      # stored as JSONB
        total_budget_usd=total_budget_usd,
        duration_days=duration_days,
        llm_model=llm_model,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_by_id(db: Session, itinerary_id: UUID) -> Optional[Itinerary]:
    return db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()


def list_for_user(db: Session, user_id: UUID) -> List[Itinerary]:
    return (
        db.query(Itinerary)
        .filter(Itinerary.user_id == user_id)
        .order_by(desc(Itinerary.created_at))
        .all()
    )


def delete(db: Session, itinerary: Itinerary) -> None:
    db.delete(itinerary)
    db.commit()