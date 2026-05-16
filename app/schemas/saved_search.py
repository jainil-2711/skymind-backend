from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator


class SavedSearchCreateRequest(BaseModel):
    origin: str
    destination: str
    depart_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    cabin_class: str = "ECONOMY"

    @field_validator("origin", "destination")
    @classmethod
    def iata_upper(cls, v: str) -> str:
        v = v.upper().strip()
        if len(v) != 3:
            raise ValueError("Must be a 3-letter IATA airport code")
        return v

    @field_validator("passengers")
    @classmethod
    def passengers_range(cls, v: int) -> int:
        if not 1 <= v <= 9:
            raise ValueError("Passengers must be between 1 and 9")
        return v

    @field_validator("cabin_class")
    @classmethod
    def cabin_upper(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in {"ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"}:
            raise ValueError("cabin_class must be ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST")
        return v

    @field_validator("return_date")
    @classmethod
    def return_after_depart(cls, v: Optional[date], info) -> Optional[date]:
        if v and "depart_date" in info.data and info.data["depart_date"]:
            if v <= info.data["depart_date"]:
                raise ValueError("return_date must be after depart_date")
        return v


class SavedSearchOut(BaseModel):
    id: UUID
    user_id: UUID
    origin_iata: str
    destination_iata: str
    depart_date: date
    return_date: Optional[date]
    passengers: int
    cabin_class: str
    created_at: datetime

    model_config = {"from_attributes": True}