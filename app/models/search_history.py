import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, SmallInteger, Boolean, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    __table_args__ = (
        # Composite index — speeds up analytics queries by route pair
        Index("ix_search_history_route", "origin_iata", "destination_iata"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,   # nullable — anonymous users can search too
        index=True,
    )
    origin_iata = Column(String(3), nullable=False)
    destination_iata = Column(String(3), nullable=False)
    result_count = Column(SmallInteger, nullable=True)
    min_price_usd = Column(Numeric(10, 2), nullable=True)
    cache_hit = Column(Boolean, nullable=True)
    searched_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="search_history")