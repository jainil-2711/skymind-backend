from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.alert import PriceAlert


def create(
    db: Session,
    user_id: UUID,
    origin: str,
    destination: str,
    target_price_usd: float,
    departure_date=None,
) -> PriceAlert:
    alert = PriceAlert(
        user_id=user_id,
        origin_iata=origin,
        destination_iata=destination,
        target_price_usd=target_price_usd,
        departure_date=departure_date,
        is_active=True,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_by_id(db: Session, alert_id: UUID) -> Optional[PriceAlert]:
    return db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()


def list_for_user(db: Session, user_id: UUID) -> List[PriceAlert]:
    return (
        db.query(PriceAlert)
        .filter(PriceAlert.user_id == user_id)
        .order_by(PriceAlert.triggered_at.desc().nullslast())
        .all()
    )


def list_active(db: Session) -> List[PriceAlert]:
    """Return all active untriggered alerts — used by the price checker."""
    return (
        db.query(PriceAlert)
        .filter(
            PriceAlert.is_active == True,
            PriceAlert.triggered_at == None,
        )
        .all()
    )


def mark_triggered(
    db: Session,
    alert: PriceAlert,
) -> PriceAlert:
    from datetime import datetime, timezone
    alert.triggered_at = datetime.now(timezone.utc)
    alert.last_checked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def mark_checked(db: Session, alert: PriceAlert) -> PriceAlert:
    from datetime import datetime, timezone
    alert.last_checked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def delete(db: Session, alert: PriceAlert) -> None:
    db.delete(alert)
    db.commit()