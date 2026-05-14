import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    __table_args__ = (
        # Enforce unique origin-destination pairs
        UniqueConstraint("origin_iata", "destination_iata", name="uq_route_origin_destination"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin_iata = Column(
        String(3),
        ForeignKey("airports.iata_code"),
        nullable=False,
        index=True,
    )
    destination_iata = Column(
        String(3),
        ForeignKey("airports.iata_code"),
        nullable=False,
    )
    distance_km = Column(Integer, nullable=True)
    avg_duration_min = Column(Integer, nullable=True)
    avg_price_usd = Column(Numeric(10, 2), nullable=True)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    price_snapshots = relationship("PriceSnapshot", back_populates="route")