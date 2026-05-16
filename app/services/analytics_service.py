"""
Analytics Service
=================
Thin orchestration layer over search_repo aggregation queries.
Keeps the router clean and makes each function independently testable.
"""

from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories import search_repo


def get_my_searches(
    db: Session,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    rows = search_repo.list_user(db, user_id, limit=limit, offset=offset)
    total = search_repo.count_user(db, user_id)
    return {
        "searches": [
            {
                "id": str(r.id),
                "origin_iata": r.origin_iata,
                "destination_iata": r.destination_iata,
                "result_count": r.result_count,
                "min_price_usd": float(r.min_price_usd) if r.min_price_usd else None,
                "cache_hit": r.cache_hit,
                "searched_at": r.searched_at,
            }
            for r in rows
        ],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        },
    }


def get_top_routes(db: Session, user_id: UUID, limit: int = 10) -> list:
    return search_repo.top_routes(db, user_id, limit=limit)


def get_price_trends(db: Session, user_id: UUID, limit: int = 10) -> list:
    return search_repo.price_trends(db, user_id, limit=limit)