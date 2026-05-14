from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import UserOut, UpdateProfileRequest
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    return ApiResponse.ok(UserOut.model_validate(current_user).model_dump())


@router.put("/me", response_model=ApiResponse)
def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile fields."""
    updated = user_repo.update_user(
        db,
        current_user,
        full_name=payload.full_name,
        home_airport=payload.home_airport,
        currency=payload.currency,
    )
    return ApiResponse.ok(UserOut.model_validate(updated).model_dump())