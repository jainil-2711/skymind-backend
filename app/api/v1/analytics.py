from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import analytics_service
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/my-searches", response_model=ApiResponse)
def my_searches(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Paginated search history for the authenticated user.
    Ordered by most recent first.
    Use limit and offset query params for pagination.
    """
    result = analytics_service.get_my_searches(
        db, user_id=current_user.id, limit=limit, offset=offset
    )
    return ApiResponse.ok(data=result["searches"], meta=result["pagination"])


@router.get("/top-routes", response_model=ApiResponse)
def top_routes(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The user's most frequently searched routes, ranked by search count.
    Also returns the lowest price ever seen and when it was last searched.
    """
    routes = analytics_service.get_top_routes(db, user_id=current_user.id, limit=limit)
    return ApiResponse.ok(
        data=routes,
        meta={"result_count": len(routes)},
    )


@router.get("/price-trends", response_model=ApiResponse)
def price_trends(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Average, minimum, and maximum prices seen per route across all searches.
    Gives a sense of price ranges the user has encountered.
    Only includes searches where a price was returned.
    """
    trends = analytics_service.get_price_trends(db, user_id=current_user.id, limit=limit)
    return ApiResponse.ok(
        data=trends,
        meta={"result_count": len(trends)},
    )