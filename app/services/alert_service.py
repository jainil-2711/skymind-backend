"""
Alert Service
=============
Business logic for price alerts.

create()     — create a new alert for a user
list_user()  — return all alerts for a user
delete()     — remove an alert (only owner can delete)
check_all()  — called by the background scheduler every 10 minutes.
               Fetches current mock prices for every active untriggered alert.
               Marks triggered_at if current best price < target_price_usd.
"""

from typing import List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.alert import PriceAlert
from app.repositories import alert_repo
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.alert import AlertCreateRequest


def create(db: Session, user_id: UUID, payload: AlertCreateRequest) -> PriceAlert:
    return alert_repo.create(
        db,
        user_id=user_id,
        origin=payload.origin,
        destination=payload.destination,
        target_price_usd=payload.target_price_usd,
        departure_date=payload.departure_date,
    )


def list_user(db: Session, user_id: UUID) -> List[PriceAlert]:
    return alert_repo.list_for_user(db, user_id)


def delete(db: Session, alert_id: UUID, user_id: UUID) -> None:
    alert = alert_repo.get_by_id(db, alert_id)
    if not alert:
        raise NotFoundException("Alert not found")
    if alert.user_id != user_id:
        raise ForbiddenException("You do not own this alert")
    alert_repo.delete(db, alert)


def check_all(db: Session) -> dict:
    """
    Called by the background scheduler every 10 minutes.
    For each active untriggered alert:
      1. Search current mock prices for that route
      2. Find the lowest per-passenger price in the result set
      3. If best price < target_price_usd → mark triggered_at
    """
    from app.services.flight_service import search as flight_search

    alerts = alert_repo.list_active(db)

    if not alerts:
        print("[AlertService] No active alerts to check.")
        return {"checked": 0, "triggered": 0, "errors": 0}

    checked = 0
    triggered = 0
    errors = 0

    # Use a fixed upcoming date for price lookups
    search_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")

    for alert in alerts:
        try:
            result = flight_search(
                origin=alert.origin_iata,
                destination=alert.destination_iata,
                departure_date=search_date,
                passengers=1,
                cabin_class="ECONOMY",
            )

            offers = result.get("offers", [])
            if not offers:
                alert_repo.mark_checked(db, alert)
                continue

            best_price = min(
                float(offer["price"]["per_passenger"])
                for offer in offers
            )

            alert_repo.mark_checked(db, alert)
            checked += 1

            if best_price < float(alert.target_price_usd):
                alert_repo.mark_triggered(db, alert)
                triggered += 1
                print(
                    f"[AlertService] TRIGGERED alert {alert.id} | "
                    f"{alert.origin_iata}→{alert.destination_iata} | "
                    f"target=${alert.target_price_usd} | "
                    f"current=${best_price:.2f}"
                )
            else:
                print(
                    f"[AlertService] CHECKED alert {alert.id} | "
                    f"{alert.origin_iata}→{alert.destination_iata} | "
                    f"target=${alert.target_price_usd} | "
                    f"best=${best_price:.2f} | not triggered"
                )

        except Exception as e:
            errors += 1
            print(f"[AlertService] ERROR checking alert {alert.id}: {e}")

    return {"checked": checked, "triggered": triggered, "errors": errors}