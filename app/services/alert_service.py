"""
Alert service — price alert CRUD and checking with email notification.
Called by APScheduler every 10 minutes via app/tasks/price_checker.py.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.external.sendgrid_client import send_price_alert_email
from app.repositories import alert_repo
from app.repositories import user_repo
from app.schemas.alert import AlertCreateRequest


def create(db: Session, user_id: UUID, payload: AlertCreateRequest):
    return alert_repo.create(
        db=db,
        user_id=user_id,
        origin=payload.origin,
        destination=payload.destination,
        target_price_usd=payload.target_price_usd,
        departure_date=payload.departure_date,
    )


def list_for_user(db: Session, user_id: UUID):
    return alert_repo.list_for_user(db, user_id)

# Alias used by the alerts router
list_user = list_for_user

def get_by_id(db: Session, alert_id: UUID):
    return alert_repo.get_by_id(db, alert_id)


def delete(db: Session, alert_id: UUID, user_id: UUID) -> bool:
    alert = alert_repo.get_by_id(db, alert_id)
    if not alert or alert.user_id != user_id:
        return False
    alert_repo.delete(db, alert)
    return True


def check_all(db: Session) -> dict:
    """
    Called by the background scheduler every 10 minutes.
    For each active untriggered alert:
      1. Search current mock prices for that route
      2. Find the lowest per-passenger price in the result set
      3. If best price < target_price_usd → mark triggered, send email
    """
    from app.services.flight_service import search as flight_search

    alerts = alert_repo.list_active(db)
    if not alerts:
        print("[AlertService] No active alerts to check.")
        return {"checked": 0, "triggered": 0, "errors": 0}

    checked   = 0
    triggered = 0
    errors    = 0

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

                user = user_repo.get_by_id(db, str(alert.user_id))
                if user:
                    sent = send_price_alert_email(
                        to_email=user.email,
                        to_name=user.full_name or user.email,
                        origin_iata=alert.origin_iata,
                        destination_iata=alert.destination_iata,
                        target_price_usd=float(alert.target_price_usd),
                        current_price_usd=best_price,
                    )
                    print(
                        f"[AlertService] Email {'sent' if sent else 'failed'} "
                        f"to {user.email}"
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