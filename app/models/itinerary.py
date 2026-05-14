import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, SmallInteger, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prompt = Column(Text, nullable=False)
    destinations = Column(JSONB, nullable=True)
    total_budget_usd = Column(Numeric(10, 2), nullable=True)
    duration_days = Column(SmallInteger, nullable=True)
    llm_model = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="itineraries")