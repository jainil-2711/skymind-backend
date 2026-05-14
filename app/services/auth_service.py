from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories import user_repo
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import ConflictException, CredentialsException, BadRequestException
from app.schemas.user import TokenOut


def register(db: Session, email: str, password: str, full_name: str | None) -> tuple[User, TokenOut]:
    """Register a new user. Raises 409 if email already exists."""
    existing = user_repo.get_by_email(db, email)
    if existing:
        raise ConflictException("An account with this email already exists")

    user = user_repo.create_user(db, email=email, password=password, full_name=full_name)
    tokens = _issue_tokens(str(user.id))
    return user, tokens


def login(db: Session, email: str, password: str) -> tuple[User, TokenOut]:
    """Authenticate a user. Raises 401 on any mismatch (never reveal which field is wrong)."""
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise CredentialsException("Invalid email or password")

    tokens = _issue_tokens(str(user.id))
    return user, tokens


def refresh(db: Session, refresh_token: str) -> TokenOut:
    """Issue a new access + refresh token pair from a valid refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise CredentialsException("Invalid or expired refresh token")

    user_id = payload.get("sub")
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise CredentialsException("User not found")

    return _issue_tokens(str(user.id))


def _issue_tokens(user_id: str) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )