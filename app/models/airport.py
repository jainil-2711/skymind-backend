from sqlalchemy import Column, String, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Airport(Base):
    __tablename__ = "airports"

    iata_code = Column(String(3), primary_key=True, nullable=False)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    country_code = Column(String(2), nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    timezone = Column(String(50), nullable=True)
    is_major = Column(Boolean, default=False, nullable=False, index=True)