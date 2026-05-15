"""
Flight Service
==============
Orchestrates the full flight search pipeline:
  1. Build Redis cache key
  2. Return cached result if available (cache HIT)
  3. Call amadeus_client.search_flights() (cache MISS)
  4. Score results via scoring engine
  5. Write scored results to Redis (TTL 10 min)
  6. Return results + cache metadata

This layer has no HTTP knowledge and no DB knowledge.
It only coordinates the external client, the scorer, and the cache.
"""

import json
import redis
from typing import Dict, Any
from app.config import get_settings
from app.external.amadeus_client import search_flights
from app.core.scoring import score_offers

settings = get_settings()

# Redis client — one connection reused across requests
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
) -> Dict[str, Any]:
    """
    Main entry point called by the router.
    Returns a dict with 'offers' (scored, sorted) and 'meta' (cache info).
    """
    key = _cache_key(origin, destination, departure_date, passengers, cabin_class)

    # ── Cache HIT ─────────────────────────────────────────────────────────
    cached = _redis.get(key)
    if cached:
        offers = json.loads(cached)
        return {
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

    # ── Cache MISS — call provider ─────────────────────────────────────────
    raw_offers = search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        passengers=passengers,
        cabin_class=cabin_class,
    )

    # ── Score and rank ─────────────────────────────────────────────────────
    scored_offers = score_offers(raw_offers)

    # ── Write to cache ─────────────────────────────────────────────────────
    _redis.setex(key, CACHE_TTL_SECONDS, json.dumps(scored_offers))

    return {
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