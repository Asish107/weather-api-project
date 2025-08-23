# app/schemas.py

"""
Pydantic schemas for API data validation and serialization.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WeatherRecordSchema(BaseModel):
    """Schema for a single daily weather record."""
    model_config = ConfigDict(from_attributes=True)

    station_id: str
    date: date
    max_temp: Optional[int]
    min_temp: Optional[int]
    precipitation: Optional[int]


class WeatherStatisticsSchema(BaseModel):
    """Schema for calculated yearly weather statistics."""
    model_config = ConfigDict(from_attributes=True)

    station_id: str
    year: int
    avg_max_temp: Optional[float]
    avg_min_temp: Optional[float]
    total_precipitation: Optional[float]