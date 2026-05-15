"""
Graph Service
=============
Manages the lifecycle of the in-memory route graph.

The graph is built once from the database and cached as a module-level variable.
All route search requests reuse the same graph object — no DB query per request.

Reload is available via reload_graph() — useful after bulk route updates
without requiring an API restart.
"""

from typing import Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.core.graph import build_graph, find_optimal_path
from app.core.exceptions import NotFoundException, BadRequestException

# Module-level graph cache — populated on first call to get_graph()
_graph: Optional[nx.DiGraph] = None


def get_graph(db: Session) -> nx.DiGraph:
    """Return the cached graph, building it from DB if not yet initialised."""
    global _graph
    if _graph is None:
        _graph = build_graph(db)
    return _graph


def reload_graph(db: Session) -> nx.DiGraph:
    """Force a graph rebuild from the database. Call after seeding new routes."""
    global _graph
    _graph = build_graph(db)
    return _graph


def search_optimal_route(
    db: Session,
    origin: str,
    destination: str,
) -> dict:
    """
    Main entry point called by the router.
    Returns the optimal route dict or raises appropriate HTTP exceptions.
    """
    if origin == destination:
        raise BadRequestException("Origin and destination must be different airports")

    graph = get_graph(db)

    if origin not in graph:
        raise NotFoundException(f"Airport {origin} has no routes in the network")
    if destination not in graph:
        raise NotFoundException(f"Airport {destination} has no routes in the network")

    result = find_optimal_path(graph, origin, destination)

    if result is None:
        raise NotFoundException(
            f"No route found between {origin} and {destination} in the current network"
        )

    return result