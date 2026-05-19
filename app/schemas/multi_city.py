from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class MultiCityRequest(BaseModel):
    origin_iata: str = Field(..., description="Home airport — start and end point of the journey")
    cities: list[str] = Field(..., min_length=2, max_length=10, description="List of IATA codes to visit")
    optimise_for: str = Field("price", description="Optimisation dimension: 'price' or 'distance'")

    @field_validator("origin_iata")
    @classmethod
    def validate_origin(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("origin_iata must be a 3-letter IATA code")
        return v

    @field_validator("cities")
    @classmethod
    def validate_cities(cls, v: list[str]) -> list[str]:
        result = []
        for c in v:
            c = c.strip().upper()
            if len(c) != 3 or not c.isalpha():
                raise ValueError(f"'{c}' is not a valid 3-letter IATA code")
            result.append(c)
        return result

    @field_validator("optimise_for")
    @classmethod
    def validate_optimise_for(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("price", "distance"):
            raise ValueError("optimise_for must be 'price' or 'distance'")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "origin_iata": "DXB",
            "cities": ["LHR", "CDG", "AMS"],
            "optimise_for": "price"
        }
    }}


class MultiCityLeg(BaseModel):
    order: int
    origin_iata: str
    destination_iata: str
    distance_km: float | None
    avg_duration_min: int | None
    avg_price_usd: float | None


class MultiCityOut(BaseModel):
    origin_iata: str
    optimise_for: str
    ordered_cities: list[str]
    legs: list[MultiCityLeg]
    total_price_usd: float
    total_distance_km: float
    total_duration_min: int
    cities_count: int