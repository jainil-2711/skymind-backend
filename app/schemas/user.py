from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ── Request schemas ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower().strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower().strip()


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    home_airport: Optional[str] = None
    currency: Optional[str] = None

    @field_validator("home_airport")
    @classmethod
    def iata_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.upper().strip()
            if len(v) != 3:
                raise ValueError("home_airport must be a 3-letter IATA code")
        return v

    @field_validator("currency")
    @classmethod
    def currency_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.upper().strip()
            if len(v) != 3:
                raise ValueError("currency must be a 3-letter ISO 4217 code")
        return v


# ── Response schemas ───────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    home_airport: Optional[str]
    currency: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthOut(BaseModel):
    user: UserOut
    tokens: TokenOut