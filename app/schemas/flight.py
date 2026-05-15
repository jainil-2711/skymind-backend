from typing import Optional, List
from datetime import date
from pydantic import BaseModel, field_validator


class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: date
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


class ScoreBreakdown(BaseModel):
    price_score: float
    duration_score: float
    stops_score: float
    weights: dict


class FlightSegment(BaseModel):
    departure: dict
    arrival: dict
    carrierCode: str
    number: str
    duration: str
    numberOfStops: int


class FlightItinerary(BaseModel):
    duration: str
    segments: List[FlightSegment]


class FlightPrice(BaseModel):
    currency: str
    total: str
    base: str
    per_passenger: str


class ScoredFlightOffer(BaseModel):
    id: str
    source: str
    score: float
    score_breakdown: ScoreBreakdown
    itineraries: List[FlightItinerary]
    price: FlightPrice
    numberOfBookableSeats: int
    cabin_class: str

    model_config = {"from_attributes": True}


class FlightSearchMeta(BaseModel):
    cache_hit: bool
    result_count: int
    origin: str
    destination: str
    departure_date: str
    passengers: int
    cabin_class: str


class FlightSearchResponse(BaseModel):
    offers: List[dict]   # raw dicts — validated loosely for flexibility
    meta: FlightSearchMeta