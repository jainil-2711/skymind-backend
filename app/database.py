from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()


# The engine is the actual connection to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    # Keep connections alive for 30 minutes
    pool_recycle=1800,
    # Log all SQL queries in development
    echo=settings.APP_ENV == "development",
)

# SessionLocal is a factory — call it to get a database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class that all ORM models inherit from
class Base(DeclarativeBase):
    pass


# Dependency — used in FastAPI routes to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()