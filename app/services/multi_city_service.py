"""
Multi-city service — orchestrates graph lookup and TSP heuristic.
No DB access beyond loading the graph. Stateless.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.graph import build_graph
from app.core.multi_city import nearest_neighbour
from app.schemas.multi_city import MultiCityLeg, MultiCityOut, MultiCityRequest


def optimise(db: Session, req: MultiCityRequest) -> MultiCityOut:
    """
    Load the route graph, run nearest-neighbour heuristic,
    and return a MultiCityOut with ordered legs and totals.

    Raises ValueError if origin or any city is not in the graph.
    """
    G = build_graph(db)

    # Validate all nodes exist in graph
    all_nodes = set(G.nodes)
    missing = []
    for iata in [req.origin_iata] + req.cities:
        if iata not in all_nodes:
            missing.append(iata)
    if missing:
        raise ValueError(
            f"The following airports are not in the route network: {', '.join(missing)}"
        )

    # Remove origin from cities list if accidentally included
    cities = [c for c in req.cities if c != req.origin_iata]

    result = nearest_neighbour(
        G=G,
        origin=req.origin_iata,
        cities=cities,
        optimise_for=req.optimise_for,
    )

    legs = [MultiCityLeg(**leg) for leg in result.legs]

    return MultiCityOut(
        origin_iata=req.origin_iata,
        optimise_for=req.optimise_for,
        ordered_cities=result.ordered_cities,
        legs=legs,
        total_price_usd=result.total_price_usd,
        total_distance_km=result.total_distance_km,
        total_duration_min=result.total_duration_min,
        cities_count=len(cities),
    )