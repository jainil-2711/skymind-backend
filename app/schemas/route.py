from typing import List
from pydantic import BaseModel, field_validator


class RouteSegment(BaseModel):
    from_airport: str
    to_airport: str
    distance_km: int
    duration_min: int
    avg_price_usd: float

    model_config = {"populate_by_name": True}


class OptimalRouteResponse(BaseModel):
    origin: str
    destination: str
    path: List[str]
    hops: int
    segments: List[dict]
    total_distance_km: int
    total_duration_min: int
    total_avg_price_usd: float
    summary: str


class RouteNetworkStats(BaseModel):
    total_airports: int
    total_routes: int
    is_connected: bool