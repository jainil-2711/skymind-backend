import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(
        UUID(as_uuid=True),
        ForeignKey("routes.id"),
        nullable=False,
        index=True,
    )
    price_usd = Column(Numeric(10, 2), nullable=False)
    departure_date = Column(Date, nullable=False)
    cabin_class = Column(String(20), nullable=False, default="ECONOMY")
    source = Column(String(20), nullable=False, default="AMADEUS")
    captured_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    route = relationship("Route", back_populates="price_snapshots")