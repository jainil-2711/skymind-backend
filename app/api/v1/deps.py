from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import CredentialsException
from app.repositories import user_repo
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — validates Bearer token, returns the authenticated User.
    Inject into any route that requires authentication:

        @router.get("/me")
        def me(user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise CredentialsException("Invalid or expired access token")

    user_id_str = payload.get("sub")
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise CredentialsException("Malformed token subject")

    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise CredentialsException("User account not found")

    return user