"""
Route Graph Engine
==================
Builds a weighted directed graph from the routes table using NetworkX.
Runs Dijkstra's shortest path algorithm to find the optimal route between
any two airports in the network.

Graph properties:
  - Directed: DXB→LHR and LHR→DXB are separate edges (both are added)
  - Edge weight: avg_price_usd (primary optimisation target)
  - Edge attributes: distance_km, duration_min stored for path reporting
  - Nodes: IATA airport codes (strings)

Interview talking point:
  Dijkstra's runs in O((V + E) log V) time. With 47 nodes and ~270 edges
  (bidirectional), this is effectively instant. The graph is built once on
  startup and held in memory — no database query per route search.
"""

import networkx as nx
from typing import Optional
from sqlalchemy.orm import Session
from app.models.route import Route


def build_graph(db: Session) -> nx.DiGraph:
    """
    Load all active routes from PostgreSQL and construct a directed graph.
    Each route row becomes two directed edges (A→B and B→A).
    Edge weight = avg_price_usd.
    """
    G = nx.DiGraph()

    routes = db.query(Route).all()

    for route in routes:
        # Forward edge: origin → destination
        G.add_edge(
            route.origin_iata,
            route.destination_iata,
            weight=float(route.avg_price_usd),
            distance_km=route.distance_km,
            duration_min=route.avg_duration_min,
            avg_price_usd=float(route.avg_price_usd),
        )
        G.add_edge(
            route.destination_iata,
            route.origin_iata,
            weight=float(route.avg_price_usd),
            distance_km=route.distance_km,
            duration_min=route.avg_duration_min,
            avg_price_usd=float(route.avg_price_usd),
        )

    return G


def find_optimal_path(
    G: nx.DiGraph,
    origin: str,
    destination: str,
) -> Optional[dict]:
    """
    Run Dijkstra's algorithm on the graph. Returns a dict with:
      - path: list of IATA codes from origin to destination
      - hops: number of intermediate airports
      - segments: list of dicts with per-leg details
      - total_distance_km
      - total_duration_min
      - total_avg_price_usd

    Returns None if no path exists between origin and destination.
    """
    if origin not in G:
        return None
    if destination not in G:
        return None

    try:
        # Dijkstra's — minimises sum of avg_price_usd across all legs
        path = nx.dijkstra_path(G, origin, destination, weight="weight")
        path_length = nx.dijkstra_path_length(G, origin, destination, weight="weight")
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

    # Build per-segment details
    segments = []
    total_distance_km = 0
    total_duration_min = 0
    total_avg_price_usd = 0.0

    for i in range(len(path) - 1):
        leg_origin = path[i]
        leg_dest = path[i + 1]
        edge_data = G[leg_origin][leg_dest]

        segments.append({
            "from": leg_origin,
            "to": leg_dest,
            "distance_km": edge_data["distance_km"],
            "duration_min": edge_data["duration_min"],
            "avg_price_usd": edge_data["avg_price_usd"],
        })
        total_distance_km += edge_data["distance_km"]
        total_duration_min += edge_data["duration_min"]
        total_avg_price_usd += edge_data["avg_price_usd"]

    return {
        "path": path,
        "hops": len(path) - 2,          # number of intermediate airports
        "segments": segments,
        "total_distance_km": total_distance_km,
        "total_duration_min": total_duration_min,
        "total_avg_price_usd": round(total_avg_price_usd, 2),
    }