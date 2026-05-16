from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services import saved_search_service, flight_service
from app.schemas.saved_search import SavedSearchCreateRequest, SavedSearchOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/saved-searches", tags=["Saved Searches"])


@router.post("", response_model=ApiResponse, status_code=201)
def create_saved_search(
    payload: SavedSearchCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a flight search configuration for later retrieval and rerun."""
    saved = saved_search_service.create(db, user_id=current_user.id, payload=payload)
    return ApiResponse.ok(SavedSearchOut.model_validate(saved).model_dump())


@router.get("", response_model=ApiResponse)
def list_saved_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved searches for the authenticated user. Most recently saved first."""
    searches = saved_search_service.list_user(db, user_id=current_user.id)
    return ApiResponse.ok([SavedSearchOut.model_validate(s).model_dump() for s in searches])


@router.get("/{saved_search_id}", response_model=ApiResponse)
def get_saved_search(
    saved_search_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve one saved search config. Does not re-run the search."""
    saved = saved_search_service.get(
        db, saved_search_id=saved_search_id, user_id=current_user.id
    )
    return ApiResponse.ok(SavedSearchOut.model_validate(saved).model_dump())


@router.post("/{saved_search_id}/rerun", response_model=ApiResponse)
def rerun_saved_search(
    saved_search_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Re-execute a saved search with the stored parameters.
    Router orchestrates between saved_search_service and flight_service —
    neither service imports the other, preserving blueprint architecture rules.
    """
    saved = saved_search_service.get(
        db, saved_search_id=saved_search_id, user_id=current_user.id
    )
    result = flight_service.search(
        origin=saved.origin_iata,
        destination=saved.destination_iata,
        departure_date=str(saved.depart_date),
        passengers=saved.passengers,
        cabin_class=saved.cabin_class,
        user_id=current_user.id,
        db=db,
    )
    return ApiResponse.ok(
        data={
            "saved_search": SavedSearchOut.model_validate(saved).model_dump(),
            "offers": result["offers"],
        },
        meta=result["meta"],
    )


@router.delete("/{saved_search_id}", status_code=204)
def delete_saved_search(
    saved_search_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saved search. Only the owner can delete. Returns 204 No Content."""
    saved_search_service.delete(
        db, saved_search_id=saved_search_id, user_id=current_user.id
    )