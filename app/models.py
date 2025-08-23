# app/models.py

"""
SQLAlchemy ORM models for the weather data application.
"""

from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class WeatherRecord(Base):
    """Represents a daily weather record for a specific station."""
    __tablename__ = 'weather_records'

    id = Column(Integer, primary_key=True)
    station_id = Column(String(11), nullable=False, index=True)
    date = Column(Date, nullable=False)
    max_temp = Column(Integer)
    min_temp = Column(Integer)
    precipitation = Column(Integer)

    __table_args__ = (
        UniqueConstraint('station_id', 'date', name='_station_date_uc'),
    )


class WeatherStatistics(Base):
    """Represents calculated yearly weather statistics for a station."""
    __tablename__ = 'weather_statistics'

    id = Column(Integer, primary_key=True)
    station_id = Column(String(11), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    avg_max_temp = Column(Float)
    avg_min_temp = Column(Float)
    total_precipitation = Column(Float)

    __table_args__ = (
        UniqueConstraint('station_id', 'year', name='_station_year_uc'),
    )