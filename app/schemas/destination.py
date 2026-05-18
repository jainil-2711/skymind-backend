from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class InspireRequest(BaseModel):
    origin_iata:  str        = Field(..., description="3-letter IATA code of departure airport")
    budget_usd:   float      = Field(..., gt=0, description="Total per-person budget in USD")
    duration_days: int       = Field(..., ge=1, le=30, description="Available trip duration in days")
    top_n:        int        = Field(10, ge=1, le=50, description="Number of top destinations to return")
    region:       str | None = Field(None, description="Optional region filter e.g. 'Europe', 'Asia'")

    @field_validator("origin_iata")
    @classmethod
    def validate_iata(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("origin_iata must be a 3-letter IATA code")
        return v

    @field_validator("budget_usd")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v < 50:
            raise ValueError("budget_usd must be at least $50")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "origin_iata": "DXB",
            "budget_usd": 600,
            "duration_days": 7,
            "top_n": 10,
            "region": None,
        }
    }}


class DestinationOut(BaseModel):
    iata:                 str
    city:                 str
    country:              str
    region:               str
    price_usd:            float
    duration_min:         int
    budget_remaining_usd: float
    price_score:          float = Field(..., description="0-1, higher = cheaper relative to pool")
    duration_score:       float = Field(..., description="0-1, higher = shorter flight relative to pool")
    value_score:          float = Field(..., description="0-1, higher = more budget left over")
    composite_score:      float = Field(..., description="Weighted average of all three scores")