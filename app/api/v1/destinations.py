from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.destination import InspireRequest
from app.services import destination_service

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.post("/inspire", summary="Flexible Destination Optimizer")
def inspire(
    req: InspireRequest,
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    The killer feature.

    Send budget, available days, and origin airport.
    SkyMind returns a ranked list of destinations scored across three
    dimensions: price efficiency, flight duration, and value (budget
    remainder ratio). Same min-max normalisation as the flight scorer.
    """
    results, meta = destination_service.inspire(req)
    return ApiResponse.ok(
        data=[r.model_dump() for r in results],
        meta=meta,
    )