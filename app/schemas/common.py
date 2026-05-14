from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Standard envelope for every response SkyMind returns."""
    success: bool
    data: Any
    meta: dict = {}

    @classmethod
    def ok(cls, data: Any, meta: dict = {}) -> "ApiResponse":
        return cls(success=True, data=data, meta=meta)

    @classmethod
    def error(cls, detail: str) -> "ApiResponse":
        return cls(success=False, data={"detail": detail}, meta={})