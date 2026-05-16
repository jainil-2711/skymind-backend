"""
Search Repository
=================
DB access for search_history table.
write()      — called by flight_service after every search
list_user()  — paginated history for one user
top_routes() — GROUP BY origin+destination, ordered by search count
price_trends() — AVG min_price_usd per route over time
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.search_history import SearchHistory


def write(
    db: Session,
    user_id: UUID,
    origin_iata: str,
    destination_iata: str,
    result_count: int,
    min_price_usd: Optional[float],
    cache_hit: bool,
) -> SearchHistory:
    row = SearchHistory(
        user_id=user_id,
        origin_iata=origin_iata,
        destination_iata=destination_iata,
        result_count=result_count,
        min_price_usd=min_price_usd,
        cache_hit=cache_hit,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_user(
    db: Session,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> List[SearchHistory]:
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user_id)
        .order_by(desc(SearchHistory.searched_at))
        .limit(limit)
        .offset(offset)
        .all()
    )


def count_user(db: Session, user_id: UUID) -> int:
    return (
        db.query(func.count(SearchHistory.id))
        .filter(SearchHistory.user_id == user_id)
        .scalar()
    )


def top_routes(
    db: Session,
    user_id: UUID,
    limit: int = 10,
) -> List[dict]:
    """
    Return the user's most searched origin→destination pairs.
    Uses GROUP BY and COUNT — pure SQL aggregation, no Python loop.
    """
    rows = (
        db.query(
            SearchHistory.origin_iata,
            SearchHistory.destination_iata,
            func.count(SearchHistory.id).label("search_count"),
            func.min(SearchHistory.min_price_usd).label("lowest_price_seen"),
            func.max(SearchHistory.searched_at).label("last_searched_at"),
        )
        .filter(SearchHistory.user_id == user_id)
        .group_by(SearchHistory.origin_iata, SearchHistory.destination_iata)
        .order_by(desc("search_count"))
        .limit(limit)
        .all()
    )
    return [
        {
            "origin_iata": r.origin_iata,
            "destination_iata": r.destination_iata,
            "search_count": r.search_count,
            "lowest_price_seen": float(r.lowest_price_seen) if r.lowest_price_seen else None,
            "last_searched_at": r.last_searched_at,
        }
        for r in rows
    ]


def price_trends(
    db: Session,
    user_id: UUID,
    limit: int = 10,
) -> List[dict]:
    """
    Return average min price seen per route across all searches.
    Gives the user a sense of typical price ranges they've encountered.
    """
    rows = (
        db.query(
            SearchHistory.origin_iata,
            SearchHistory.destination_iata,
            func.count(SearchHistory.id).label("search_count"),
            func.avg(SearchHistory.min_price_usd).label("avg_price_usd"),
            func.min(SearchHistory.min_price_usd).label("min_price_usd"),
            func.max(SearchHistory.min_price_usd).label("max_price_usd"),
        )
        .filter(
            SearchHistory.user_id == user_id,
            SearchHistory.min_price_usd != None,
        )
        .group_by(SearchHistory.origin_iata, SearchHistory.destination_iata)
        .order_by(desc("search_count"))
        .limit(limit)
        .all()
    )
    return [
        {
            "origin_iata": r.origin_iata,
            "destination_iata": r.destination_iata,
            "search_count": r.search_count,
            "avg_price_usd": round(float(r.avg_price_usd), 2) if r.avg_price_usd else None,
            "min_price_usd": float(r.min_price_usd) if r.min_price_usd else None,
            "max_price_usd": float(r.max_price_usd) if r.max_price_usd else None,
        }
        for r in rows
    ]