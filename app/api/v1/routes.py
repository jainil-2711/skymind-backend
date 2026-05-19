from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.multi_city import MultiCityRequest
from app.services import graph_service
from app.services import multi_city_service

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
    Optimises for total estimated price across all legs.
    """
    origin      = origin.upper().strip()
    destination = destination.upper().strip()
    result      = graph_service.search_optimal_route(db, origin, destination)

    path_str = " → ".join(result["path"])
    hours    = result["total_duration_min"] // 60
    mins     = result["total_duration_min"] % 60
    summary  = (
        f"{path_str} | "
        f"{result['hops']} stop{'s' if result['hops'] != 1 else ''} | "
        f"{hours}h {mins}m total | "
        f"~${result['total_avg_price_usd']:.0f} USD"
    )
    return ApiResponse.ok(
        data={
            "origin":               origin,
            "destination":          destination,
            "path":                 result["path"],
            "hops":                 result["hops"],
            "segments":             result["segments"],
            "total_distance_km":    result["total_distance_km"],
            "total_duration_min":   result["total_duration_min"],
            "total_avg_price_usd":  result["total_avg_price_usd"],
            "summary":              summary,
        }
    )


@router.get("/network/stats", response_model=ApiResponse)
def get_network_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return statistics about the current route graph."""
    import networkx as nx
    graph = graph_service.get_graph(db)
    return ApiResponse.ok(
        data={
            "total_airports":      graph.number_of_nodes(),
            "total_routes":        graph.number_of_edges(),
            "is_weakly_connected": nx.is_weakly_connected(graph),
            "airport_codes":       sorted(list(graph.nodes())),
        }
    )


@router.post("/graph/reload", response_model=ApiResponse)
def reload_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force a graph reload from the database."""
    graph = graph_service.reload_graph(db)
    return ApiResponse.ok(
        data={
            "message":        "Graph reloaded successfully",
            "total_airports": graph.number_of_nodes(),
            "total_routes":   graph.number_of_edges(),
        }
    )


@router.post("/multi-city", response_model=ApiResponse)
def multi_city_optimise(
    req: MultiCityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Multi-city route optimizer.

    Given a home airport and a list of cities, finds the optimal visitation
    order using a nearest-neighbour TSP heuristic on the route graph.
    Returns to origin at the end.

    Example: DXB → LHR → CDG → AMS → DXB optimised for price.
    """
    try:
        result = multi_city_service.optimise(db, req)
    except ValueError as e:
        return ApiResponse.error(detail=str(e))

    return ApiResponse.ok(
        data=result.model_dump(),
        meta={
            "optimise_for": req.optimise_for,
            "cities_count": result.cities_count,
        }
    )