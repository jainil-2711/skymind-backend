from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, field_validator


class ItineraryLeg(BaseModel):
    """
    One stop in the itinerary.
    Stored as a JSONB array element in the destinations column.
    """
    order: int                          # 1-based position in the trip
    origin_iata: str
    destination_iata: str
    depart_date: str                    # ISO date string e.g. "2025-12-01"
    cabin_class: str = "ECONOMY"
    estimated_price_usd: Optional[float] = None
    duration_min: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("origin_iata", "destination_iata")
    @classmethod
    def iata_upper(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) != 3:
            raise ValueError("Must be a 3-letter IATA airport code")
        return v

    @field_validator("cabin_class")
    @classmethod
    def cabin_upper(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in {"ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"}:
            raise ValueError("Must be ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST")
        return v


class ItineraryCreateRequest(BaseModel):
    prompt: Optional[str] = None        # free-text description of the trip
    destinations: List[ItineraryLeg]    # ordered list of legs
    total_budget_usd: Optional[float] = None
    duration_days: Optional[int] = None

    @field_validator("destinations")
    @classmethod
    def at_least_one_leg(cls, v: List[ItineraryLeg]) -> List[ItineraryLeg]:
        if len(v) < 1:
            raise ValueError("Itinerary must have at least one leg")
        return v

    @field_validator("total_budget_usd")
    @classmethod
    def budget_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("total_budget_usd must be greater than 0")
        return v

    @field_validator("duration_days")
    @classmethod
    def duration_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("duration_days must be greater than 0")
        return v


class ItineraryOut(BaseModel):
    id: UUID
    user_id: UUID
    prompt: Optional[str]
    destinations: List[Any]             # raw JSONB — list of leg dicts
    total_budget_usd: Optional[float]
    duration_days: Optional[int]
    llm_model: Optional[str]
    created_at: datetime

    # Calculated fields — not stored in DB, computed on read
    total_legs: int
    total_estimated_price_usd: Optional[float]
    total_duration_min: Optional[int]

    model_config = {"from_attributes": True}