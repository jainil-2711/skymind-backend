"""
Three-dimension destination scorer using min-max normalisation.
Same pattern as app/core/scoring.py — intentional consistency.

price_score   : lower price  → higher score (inverted min-max)
duration_score: shorter flight → higher score (inverted min-max)
value_score   : larger budget remainder ratio → higher score (direct min-max)
composite_score: equal-weighted average of all three
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoredDestination:
    iata: str
    city: str
    country: str
    region: str
    price_usd: float
    duration_min: int
    price_score: float
    duration_score: float
    value_score: float
    composite_score: float
    budget_remaining_usd: float


def _min_max(values: list[float]) -> list[float]:
    """Normalise a list of floats to [0, 1]. Returns 0.5 for flat lists."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def rank_destinations(
    candidates: list[dict[str, Any]],
    budget_usd: float,
    weights: dict[str, float] | None = None,
) -> list[ScoredDestination]:
    """
    Score and rank candidate destination dicts.
    candidates must have: iata, city, country, region, price_usd, duration_min.
    Returns list of ScoredDestination sorted by composite_score descending.
    """
    if not candidates:
        return []

    w = weights or {"price": 1 / 3, "duration": 1 / 3, "value": 1 / 3}

    prices     = [c["price_usd"] for c in candidates]
    durations  = [float(c["duration_min"]) for c in candidates]
    remainders = [(budget_usd - c["price_usd"]) / budget_usd for c in candidates]

    price_norms    = [1.0 - v for v in _min_max(prices)]
    duration_norms = [1.0 - v for v in _min_max(durations)]
    value_norms    = _min_max(remainders)

    scored: list[ScoredDestination] = []
    for i, c in enumerate(candidates):
        ps = round(price_norms[i], 4)
        ds = round(duration_norms[i], 4)
        vs = round(value_norms[i], 4)
        composite = round(w["price"] * ps + w["duration"] * ds + w["value"] * vs, 4)
        scored.append(ScoredDestination(
            iata=c["iata"],
            city=c["city"],
            country=c["country"],
            region=c["region"],
            price_usd=round(c["price_usd"], 2),
            duration_min=int(c["duration_min"]),
            price_score=ps,
            duration_score=ds,
            value_score=vs,
            composite_score=composite,
            budget_remaining_usd=round(budget_usd - c["price_usd"], 2),
        ))

    scored.sort(key=lambda x: x.composite_score, reverse=True)
    return scored