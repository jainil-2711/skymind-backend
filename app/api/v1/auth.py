from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service
from app.schemas.user import RegisterRequest, LoginRequest, RefreshRequest, AuthOut, TokenOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new account.
    Returns the user profile + JWT token pair on success.
    """
    user, tokens = auth_service.register(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return ApiResponse.ok(
        AuthOut(
            user=user,
            tokens=tokens,
        ).model_dump()
    )


@router.post("/login", response_model=ApiResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email + password.
    Returns the user profile + JWT token pair on success.
    """
    user, tokens = auth_service.login(db, email=payload.email, password=payload.password)
    return ApiResponse.ok(
        AuthOut(
            user=user,
            tokens=tokens,
        ).model_dump()
    )


@router.post("/refresh", response_model=ApiResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Use this when the access token expires (30 min TTL).
    """
    tokens = auth_service.refresh(db, refresh_token=payload.refresh_token)
    return ApiResponse.ok(tokens.model_dump())


@router.post("/logout", response_model=ApiResponse)
def logout():
    """
    Logout is handled client-side — delete both tokens from storage.
    This endpoint exists for API completeness and future server-side blocklist.
    """
    return ApiResponse.ok({"message": "Logged out successfully"})