"""
Flight Service
==============
Orchestrates the full flight search pipeline:
  1. Build Redis cache key
  2. Return cached result if available (cache HIT)
  3. Call amadeus_client.search_flights() (cache MISS)
  4. Score results via scoring engine
  5. Write scored results to Redis (TTL 10 min)
  6. Log the search to search_history (Week 7)
  7. Return results + cache metadata

Week 7 addition: search logging is fire-and-forget.
If the DB write fails, the search result is still returned.
The user experience is never degraded by a logging failure.
"""

import json
import redis
from typing import Optional, Dict, Any
from uuid import UUID
from app.config import get_settings
from app.external.amadeus_client import search_flights
from app.core.scoring import score_offers

settings = get_settings()

_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

CACHE_TTL_SECONDS = 600  # 10 minutes


def _cache_key(origin: str, destination: str, date: str, passengers: int, cabin: str) -> str:
    return f"flights:{origin.upper()}:{destination.upper()}:{date}:{passengers}:{cabin.upper()}"


def search(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1,
    cabin_class: str = "ECONOMY",
    user_id: Optional[UUID] = None,
    db=None,
) -> Dict[str, Any]:
    """
    Main entry point called by the router and the alert checker.
    user_id and db are optional — if provided, the search is logged.
    The alert checker calls without user_id/db so it doesn't pollute history.
    """
    key = _cache_key(origin, destination, departure_date, passengers, cabin_class)

    # ── Cache HIT ─────────────────────────────────────────────────────────
    cached = _redis.get(key)
    if cached:
        offers = json.loads(cached)
        result = {
            "offers": offers,
            "meta": {
                "cache_hit": True,
                "result_count": len(offers),
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date,
                "passengers": passengers,
                "cabin_class": cabin_class.upper(),
            },
        }
        _log_search(db, user_id, origin, destination, offers, cache_hit=True)
        return result

    # ── Cache MISS ────────────────────────────────────────────────────────
    raw_offers = search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        passengers=passengers,
        cabin_class=cabin_class,
    )

    scored_offers = score_offers(raw_offers)
    _redis.setex(key, CACHE_TTL_SECONDS, json.dumps(scored_offers))

    result = {
        "offers": scored_offers,
        "meta": {
            "cache_hit": False,
            "result_count": len(scored_offers),
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "passengers": passengers,
            "cabin_class": cabin_class.upper(),
        },
    }
    _log_search(db, user_id, origin, destination, scored_offers, cache_hit=False)
    return result


def _log_search(db, user_id, origin, destination, offers, cache_hit):
    """
    Fire-and-forget search logging.
    Only runs when both db and user_id are provided.
    Exceptions are swallowed — logging must never break the search response.
    """
    if db is None or user_id is None:
        return
    try:
        from app.repositories import search_repo
        min_price = None
        if offers:
            prices = [
                float(o["price"]["per_passenger"])
                for o in offers
                if o.get("price", {}).get("per_passenger")
            ]
            if prices:
                min_price = min(prices)

        search_repo.write(
            db=db,
            user_id=user_id,
            origin_iata=origin.upper(),
            destination_iata=destination.upper(),
            result_count=len(offers),
            min_price_usd=min_price,
            cache_hit=cache_hit,
        )
    except Exception as e:
        print(f"[FlightService] Search logging failed (non-fatal): {e}")