from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services import planner_service

router = APIRouter(prefix="/planner", tags=["Planner"])


class GenerateRequest(BaseModel):
    prompt: str
    total_budget_usd: float | None = None
    duration_days: int | None = None


@router.post("/generate", summary="AI Trip Planner — natural language to structured itinerary")
def generate(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """
    Send a free-text trip description.
    SkyMind calls the Claude API and returns a structured multi-leg
    itinerary stored in the itineraries table with llm_model populated.

    Example: "10 days in Europe from Dubai, London Paris Rome, economy, budget $2000"
    """
    try:
        result = planner_service.generate(
            db=db,
            user_id=str(current_user.id),
            prompt=req.prompt,
            total_budget_usd=req.total_budget_usd,
            duration_days=req.duration_days,
        )
    except ValueError as e:
        return ApiResponse.error(detail=str(e))
    except RuntimeError as e:
        return ApiResponse.error(detail=str(e))

    return ApiResponse.ok(
        data=result.model_dump(),
        meta={"llm_model": result.llm_model},
    )