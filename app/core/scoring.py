"""
Flight Scoring Engine
=====================
Converts raw Amadeus flight offer data into a normalised composite score (0.0 – 1.0).

Score dimensions:
  - Price score      (40% weight) — cheaper is better
  - Duration score   (35% weight) — shorter is better
  - Stops score      (25% weight) — fewer stops is better

Min-max normalisation: best offer in the result set scores 1.0, worst scores 0.0.
Final score = weighted sum of the three normalised dimensions.

Interview talking point:
  This is the same pattern used in recommendation systems. The weights are
  configurable — a future feature could let users set their own weight preferences
  (e.g. "I care more about price than duration").
"""

from typing import List, Dict, Any

WEIGHT_PRICE = 0.40
WEIGHT_DURATION = 0.35
WEIGHT_STOPS = 0.25


def _parse_duration_minutes(iso_duration: str) -> int:
    """
    Convert ISO 8601 duration string to total minutes.
    e.g. 'PT7H30M' → 450,  'PT1H' → 60,  'PT45M' → 45
    """
    import re
    hours = int(re.search(r'(\d+)H', iso_duration).group(1)) if 'H' in iso_duration else 0
    minutes = int(re.search(r'(\d+)M', iso_duration).group(1)) if 'M' in iso_duration else 0
    return hours * 60 + minutes


def _minmax_normalise(values: List[float], invert: bool = False) -> List[float]:
    """
    Normalise a list of floats to [0.0, 1.0].
    invert=True means lower raw value → higher score (used for price, duration, stops).
    If all values are identical, return 1.0 for all (everyone ties at best).
    """
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return [1.0] * len(values)

    if invert:
        return [(max_val - v) / (max_val - min_val) for v in values]
    else:
        return [(v - min_val) / (max_val - min_val) for v in values]


def score_offers(offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Accept a list of raw flight offer dicts and return the same list with
    a 'score' field (float, 0.0–1.0) and 'score_breakdown' dict added to each.
    List is returned sorted by score descending (best first).
    """
    if not offers:
        return []

    # Extract raw dimensions from each offer
    prices = [float(offer["price"]["total"]) for offer in offers]
    durations = [
        _parse_duration_minutes(offer["itineraries"][0]["duration"])
        for offer in offers
    ]
    stops = [
        len(offer["itineraries"][0]["segments"]) - 1
        for offer in offers
    ]

    # Normalise each dimension (lower raw value → higher score)
    price_scores = _minmax_normalise(prices, invert=True)
    duration_scores = _minmax_normalise(durations, invert=True)
    stops_scores = _minmax_normalise([float(s) for s in stops], invert=True)

    # Apply weights and attach scores to offers
    scored = []
    for i, offer in enumerate(offers):
        composite = (
            WEIGHT_PRICE * price_scores[i]
            + WEIGHT_DURATION * duration_scores[i]
            + WEIGHT_STOPS * stops_scores[i]
        )
        scored.append({
            **offer,
            "score": round(composite, 4),
            "score_breakdown": {
                "price_score": round(price_scores[i], 4),
                "duration_score": round(duration_scores[i], 4),
                "stops_score": round(stops_scores[i], 4),
                "weights": {
                    "price": WEIGHT_PRICE,
                    "duration": WEIGHT_DURATION,
                    "stops": WEIGHT_STOPS,
                },
            },
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)