from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import alert_service
from app.schemas.alert import AlertCreateRequest, AlertOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=ApiResponse, status_code=201)
def create_alert(
    payload: AlertCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a price alert for a route.
    The alert is marked triggered when the best available price
    drops below your target_price_usd. Requires authentication.
    """
    alert = alert_service.create(db, user_id=current_user.id, payload=payload)
    return ApiResponse.ok(AlertOut.model_validate(alert).model_dump())


@router.get("", response_model=ApiResponse)
def list_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all price alerts for the authenticated user."""
    alerts = alert_service.list_user(db, user_id=current_user.id)
    return ApiResponse.ok([AlertOut.model_validate(a).model_dump() for a in alerts])


@router.delete("/{alert_id}", status_code=204)
def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a price alert. Only the owner can delete their own alert.
    Returns 204 No Content on success.
    """
    alert_service.delete(db, alert_id=alert_id, user_id=current_user.id)


@router.post("/check", response_model=ApiResponse)
def trigger_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger the price check for all active alerts.
    Normally runs automatically every 10 minutes via APScheduler.
    Use this to test alert triggering without waiting.
    """
    result = alert_service.check_all(db)
    return ApiResponse.ok(result)