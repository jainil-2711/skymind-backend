from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# Password hashing — bcrypt with auto-upgrade
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create a short-lived JWT access token (30 min)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,       # subject = user UUID as string
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived JWT refresh token (7 days)."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload dict or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None