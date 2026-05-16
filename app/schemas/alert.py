from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator


class AlertCreateRequest(BaseModel):
    origin: str
    destination: str
    target_price_usd: float
    departure_date: Optional[date] = None

    @field_validator("origin", "destination")
    @classmethod
    def iata_upper(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) != 3:
            raise ValueError("Must be a 3-letter IATA airport code")
        return v

    @field_validator("target_price_usd")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("target_price_usd must be greater than 0")
        return round(v, 2)


class AlertOut(BaseModel):
    id: UUID
    user_id: UUID
    origin_iata: str
    destination_iata: str
    target_price_usd: float
    departure_date: Optional[date]
    is_active: bool
    last_checked_at: Optional[datetime]
    triggered_at: Optional[datetime]

    model_config = {"from_attributes": True}