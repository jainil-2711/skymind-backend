import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    origin_iata = Column(String(3), nullable=False)
    destination_iata = Column(String(3), nullable=False)
    depart_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)
    passengers = Column(SmallInteger, nullable=False, default=1)
    cabin_class = Column(String(20), nullable=False, default="ECONOMY")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="saved_searches")