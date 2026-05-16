from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SearchHistoryItem(BaseModel):
    id: str
    origin_iata: str
    destination_iata: str
    result_count: int
    min_price_usd: Optional[float]
    cache_hit: bool
    searched_at: datetime

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class MySearchesResponse(BaseModel):
    searches: List[SearchHistoryItem]
    pagination: PaginationMeta


class TopRouteItem(BaseModel):
    origin_iata: str
    destination_iata: str
    search_count: int
    lowest_price_seen: Optional[float]
    last_searched_at: Optional[datetime]


class PriceTrendItem(BaseModel):
    origin_iata: str
    destination_iata: str
    search_count: int
    avg_price_usd: Optional[float]
    min_price_usd: Optional[float]
    max_price_usd: Optional[float]