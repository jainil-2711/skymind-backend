from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        full_name=full_name,
        currency="USD",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, **kwargs) -> User:
    for field, value in kwargs.items():
        if value is not None and hasattr(user, field):
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user