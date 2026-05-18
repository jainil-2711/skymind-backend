"""
Planner service — orchestrates AI trip generation via the Claude client.

Flow
----
1. Call claude_client.generate_itinerary() with the raw prompt
2. Validate each returned leg against ItineraryLeg schema
3. Persist to the itineraries table via itinerary_repo
4. Return the saved itinerary with computed totals

Architecture note: claude_client is the only external call — lives in
app/external/ as required. This service never imports other services.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.external.claude_client import CLAUDE_MODEL, generate_itinerary
from app.repositories.itinerary_repo import create, get_by_id
from app.schemas.itinerary import ItineraryLeg, ItineraryOut
from app.services.itinerary_service import _compute


def generate(
    db: Session,
    user_id: str,
    prompt: str,
    total_budget_usd: float | None,
    duration_days: int | None,
) -> ItineraryOut:
    """
    Generate a structured itinerary from a natural language prompt,
    persist it, and return it with computed totals.

    Raises
    ------
    ValueError  — Claude returned malformed JSON or invalid leg data
    RuntimeError — CLAUDE_API_KEY missing (real mode only)
    """
    # 1. Call Claude
    raw_legs = generate_itinerary(prompt)

    # 2. Validate each leg through the existing Pydantic schema
    validated_legs = []
    for leg in raw_legs:
        try:
            validated_legs.append(ItineraryLeg(**leg).model_dump())
        except Exception as e:
            raise ValueError(f"Claude returned an invalid leg: {leg} — {e}")

    # 3. Derive budget and duration from legs if not supplied by caller
    if total_budget_usd is None:
        total_budget_usd = float(
            sum(leg.get("estimated_price_usd", 0) for leg in validated_legs)
        )
    if duration_days is None:
        duration_days = len(validated_legs)

    # 4. Persist via existing itinerary_repo
    itinerary = create(
        db=db,
        user_id=user_id,
        prompt=prompt,
        destinations=validated_legs,
        total_budget_usd=total_budget_usd,
        duration_days=duration_days,
        llm_model=CLAUDE_MODEL,
    )

    # 5. Fetch back and return with computed totals
    saved = get_by_id(db, str(itinerary.id))
    computed = _compute(saved)

    return ItineraryOut(**computed)