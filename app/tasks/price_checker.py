"""
Price Checker — Background Scheduler
=====================================
Uses APScheduler to run alert_service.check_all() every 10 minutes.

The scheduler is started when the FastAPI app starts (via lifespan) and
stopped cleanly when the app shuts down.

This is the first component in SkyMind that runs independently of any
HTTP request — a background worker pattern used in every production system.

Interview talking point:
  APScheduler runs in the same process as the API. For higher scale,
  this would move to a Celery worker with Redis as the broker — the
  alert_service.check_all() function would become a Celery task with
  zero changes to its internal logic.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()


def run_price_check():
    """
    Wrapper called by APScheduler.
    Creates its own DB session — schedulers run outside the request lifecycle
    so they cannot use FastAPI's Depends(get_db).
    """
    from app.database import SessionLocal
    from app.services.alert_service import check_all

    db = SessionLocal()
    try:
        print("[PriceChecker] Running scheduled price check...")
        result = check_all(db)
        print(
            f"[PriceChecker] Done — "
            f"checked={result['checked']} "
            f"triggered={result['triggered']} "
            f"errors={result['errors']}"
        )
    except Exception as e:
        print(f"[PriceChecker] Scheduler error: {e}")
    finally:
        db.close()


def start():
    """Start the background scheduler. Called from app lifespan."""
    scheduler.add_job(
        run_price_check,
        trigger=IntervalTrigger(minutes=10),
        id="price_checker",
        name="Price Alert Checker",
        replace_existing=True,
    )
    scheduler.start()
    print("[PriceChecker] Scheduler started — running every 10 minutes")


def stop():
    """Stop the scheduler cleanly. Called from app lifespan."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[PriceChecker] Scheduler stopped")