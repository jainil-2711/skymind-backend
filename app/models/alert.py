import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    origin_iata = Column(String(3), nullable=False)
    destination_iata = Column(String(3), nullable=False)
    target_price_usd = Column(Numeric(10, 2), nullable=False)
    departure_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True, index=True)
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="price_alerts")