"""
Destination service — business logic for the Flexible Destination Optimizer.

Flow
----
1. Call inspiration_client.get_inspiration() — raw ~50 destination candidates
2. Hard filter: price_usd <= budget_usd  (over-budget destinations removed)
3. Optional region filter if req.region is set
4. Score with destination_ranker.rank_destinations()
5. Slice top_n and serialise to DestinationOut

Stateless — no DB access. Safe to call from any context.
"""
from __future__ import annotations

from app.core.destination_ranker import rank_destinations
from app.external.inspiration_client import get_inspiration
from app.schemas.destination import DestinationOut, InspireRequest


def inspire(req: InspireRequest) -> tuple[list[DestinationOut], dict]:
    """
    Return (ranked_destinations, meta) for the given InspireRequest.

    meta keys: origin_iata, budget_usd, duration_days,
               total_candidates, after_budget_filter,
               after_region_filter, returned
    """
    raw = get_inspiration(req.origin_iata, max_results=50)
    total_candidates = len(raw)

    affordable = [c for c in raw if c["price_usd"] <= req.budget_usd]
    after_budget = len(affordable)

    if req.region:
        region_norm = req.region.strip().title()
        affordable = [c for c in affordable if c["region"] == region_norm]
    after_region = len(affordable)

    ranked = rank_destinations(affordable, budget_usd=req.budget_usd)
    top = ranked[: req.top_n]

    results = [
        DestinationOut(
            iata=d.iata,
            city=d.city,
            country=d.country,
            region=d.region,
            price_usd=d.price_usd,
            duration_min=d.duration_min,
            budget_remaining_usd=d.budget_remaining_usd,
            price_score=d.price_score,
            duration_score=d.duration_score,
            value_score=d.value_score,
            composite_score=d.composite_score,
        )
        for d in top
    ]

    meta = {
        "origin_iata":         req.origin_iata,
        "budget_usd":          req.budget_usd,
        "duration_days":       req.duration_days,
        "total_candidates":    total_candidates,
        "after_budget_filter": after_budget,
        "after_region_filter": after_region,
        "returned":            len(results),
    }

    return results, meta