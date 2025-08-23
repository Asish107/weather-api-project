# app/api.py

"""
RESTful API for the weather data application using FastAPI.
Exposes endpoints for raw weather records and calculated yearly statistics.
"""

from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db

app = FastAPI(
    title="Weather Data API",
    description="An API for accessing weather and statistics data.",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """A simple root endpoint to confirm that the API is running."""
    return {"message": "Welcome to the Weather API! Visit /docs for documentation."}


@app.get("/api/weather", response_model=List[schemas.WeatherRecordSchema])
def get_weather_records(
    station_id: Optional[str] = None,
    date: Optional[str] = None,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve paginated daily weather records, with optional filters."""
    query = db.query(models.WeatherRecord)

    if station_id:
        query = query.filter(models.WeatherRecord.station_id == station_id)
    if date:
        query = query.filter(models.WeatherRecord.date == date)

    records = query.offset((page - 1) * page_size).limit(page_size).all()
    return records


@app.get("/api/weather/stats", response_model=List[schemas.WeatherStatisticsSchema])
def get_weather_statistics(
    station_id: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve paginated yearly weather statistics, with optional filters."""
    query = db.query(models.WeatherStatistics)

    if station_id:
        query = query.filter(models.WeatherStatistics.station_id == station_id)
    if year:
        query = query.filter(models.WeatherStatistics.year == year)

    stats = query.offset((page - 1) * page_size).limit(page_size).all()
    return stats