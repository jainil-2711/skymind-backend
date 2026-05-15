from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import graph_service
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/optimal", response_model=ApiResponse)
def get_optimal_route(
    origin: str = Query(..., min_length=3, max_length=3, description="Origin IATA airport code"),
    destination: str = Query(..., min_length=3, max_length=3, description="Destination IATA airport code"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Find the optimal route between two airports using Dijkstra's algorithm.

    - Optimises for total estimated price across all legs
    - Returns full path with per-segment breakdown
    - Graph is loaded from the database once on first request and cached in memory
    - Requires authentication
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    result = graph_service.search_optimal_route(db, origin, destination)

    # Build a human-readable summary
    path_str = " → ".join(result["path"])
    hours = result["total_duration_min"] // 60
    mins = result["total_duration_min"] % 60
    summary = (
        f"{path_str} | "
        f"{result['hops']} stop{'s' if result['hops'] != 1 else ''} | "
        f"{hours}h {mins}m total | "
        f"~${result['total_avg_price_usd']:.0f} USD"
    )

    return ApiResponse.ok(
        data={
            "origin": origin,
            "destination": destination,
            "path": result["path"],
            "hops": result["hops"],
            "segments": result["segments"],
            "total_distance_km": result["total_distance_km"],
            "total_duration_min": result["total_duration_min"],
            "total_avg_price_usd": result["total_avg_price_usd"],
            "summary": summary,
        }
    )


@router.get("/network/stats", response_model=ApiResponse)
def get_network_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return statistics about the current route graph.
    Useful for debugging and for the frontend dashboard.
    """
    import networkx as nx
    graph = graph_service.get_graph(db)

    return ApiResponse.ok(
        data={
            "total_airports": graph.number_of_nodes(),
            "total_routes": graph.number_of_edges(),
            "is_weakly_connected": nx.is_weakly_connected(graph),
            "airport_codes": sorted(list(graph.nodes())),
        }
    )


@router.post("/graph/reload", response_model=ApiResponse)
def reload_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Force a graph reload from the database.
    Call this after seeding new routes without restarting the API.
    """
    graph = graph_service.reload_graph(db)
    return ApiResponse.ok(
        data={
            "message": "Graph reloaded successfully",
            "total_airports": graph.number_of_nodes(),
            "total_routes": graph.number_of_edges(),
        }
    )