"""
Multi-city route optimizer using a nearest-neighbour TSP heuristic.
Builds on the existing NetworkX DiGraph from app/core/graph.py.

Algorithm
---------
Nearest-neighbour greedy heuristic:
  1. Start at origin
  2. At each step, pick the unvisited city with the lowest edge weight
     (price or distance depending on optimise_for)
  3. Repeat until all cities visited
  4. Return to origin

This is O(n²) and gives a good-enough solution for n ≤ 10 cities.
For a resume-quality project, this is the right tradeoff — TSP is NP-hard
and exact solvers are overkill for a flight planner with ≤ 10 stops.

If a direct edge does not exist between two cities, Dijkstra's shortest
path is used to find the cheapest/shortest indirect connection, using
the same graph.build_graph() that powers the Week 5 route optimizer.
"""
from __future__ import annotations

import networkx as nx
from dataclasses import dataclass, field


@dataclass
class OptimizedRoute:
    ordered_cities: list[str]
    legs: list[dict]
    total_price_usd: float
    total_distance_km: float
    total_duration_min: int


def _edge_weight(G: nx.DiGraph, src: str, dst: str, optimise_for: str) -> float:
    """
    Return the cost of travelling from src to dst.
    Uses direct edge if available, otherwise Dijkstra shortest path.
    Weight attribute: avg_price_usd for price, distance_km for distance.
    """
    attr = "avg_price_usd" if optimise_for == "price" else "distance_km"

    if G.has_edge(src, dst):
        return float(G[src][dst].get(attr, 0) or 0)

    try:
        path = nx.dijkstra_path(G, src, dst, weight=attr)
        total = 0.0
        for a, b in zip(path, path[1:]):
            total += float(G[a][b].get(attr, 0) or 0)
        return total
    except nx.NetworkXNoPath:
        return float("inf")


def _get_edge_attrs(G: nx.DiGraph, src: str, dst: str) -> dict:
    """Return edge attributes for a direct or synthetic (Dijkstra) leg."""
    if G.has_edge(src, dst):
        e = G[src][dst]
        return {
            "distance_km":    float(e.get("distance_km", 0) or 0),
            "avg_duration_min": int(e.get("duration_min", 0) or 0),
            "avg_price_usd":  float(e.get("avg_price_usd", 0) or 0),
        }

    # Synthetic leg — sum attributes along Dijkstra path
    try:
        path = nx.dijkstra_path(G, src, dst, weight="avg_price_usd")
        dist = dur = price = 0.0
        for a, b in zip(path, path[1:]):
            e = G[a][b]
            dist  += float(e.get("distance_km", 0) or 0)
            dur   += float(e.get("duration_min", 0) or 0)
            price += float(e.get("avg_price_usd", 0) or 0)
        return {
            "distance_km":      round(dist, 2),
            "avg_duration_min": int(dur),
            "avg_price_usd":    round(price, 2),
        }
    except nx.NetworkXNoPath:
        return {"distance_km": None, "avg_duration_min": None, "avg_price_usd": None}


def nearest_neighbour(
    G: nx.DiGraph,
    origin: str,
    cities: list[str],
    optimise_for: str = "price",
) -> OptimizedRoute:
    """
    Run nearest-neighbour TSP heuristic.

    Parameters
    ----------
    G            : DiGraph from graph.build_graph()
    origin       : home airport IATA — start and end of journey
    cities       : list of IATA codes to visit (excluding origin)
    optimise_for : 'price' or 'distance'

    Returns
    -------
    OptimizedRoute with ordered_cities, legs, and totals
    """
    unvisited = list(cities)
    current   = origin
    ordered   = []
    legs      = []
    order     = 1

    while unvisited:
        # Find nearest unvisited city by edge weight
        next_city = min(
            unvisited,
            key=lambda c: _edge_weight(G, current, c, optimise_for)
        )
        attrs = _get_edge_attrs(G, current, next_city)
        legs.append({
            "order":            order,
            "origin_iata":      current,
            "destination_iata": next_city,
            **attrs,
        })
        ordered.append(next_city)
        unvisited.remove(next_city)
        current = next_city
        order  += 1

    # Return leg: last city → origin
    attrs = _get_edge_attrs(G, current, origin)
    legs.append({
        "order":            order,
        "origin_iata":      current,
        "destination_iata": origin,
        **attrs,
    })

    total_price    = round(sum(l["avg_price_usd"]    or 0 for l in legs), 2)
    total_distance = round(sum(l["distance_km"]      or 0 for l in legs), 2)
    total_duration = int(sum(l["avg_duration_min"]   or 0 for l in legs))

    return OptimizedRoute(
        ordered_cities=ordered,
        legs=legs,
        total_price_usd=total_price,
        total_distance_km=total_distance,
        total_duration_min=total_duration,
    )