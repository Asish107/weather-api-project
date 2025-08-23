# tests/test_api.py

"""
Unit tests for the FastAPI application endpoints using pytest and TestClient.
Tests run against a separate, in-memory database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import app
from app.db import get_db
from app.models import Base, WeatherRecord, WeatherStatistics
from datetime import date

# 1. Define an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Pytest fixture to set up and tear down the database for each test function
@pytest.fixture(scope="function")
def db_session():
    # Create all tables in the in-memory database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test is done to ensure isolation
        Base.metadata.drop_all(bind=engine)


# 3. Override the 'get_db' dependency to use the test database for API calls
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# 4. Your original 6 tests, now updated to use the isolated database
def test_read_root():
    """Tests the root endpoint to ensure the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Weather API! Visit /docs for documentation."}


def test_get_weather_records_success(db_session):
    """Tests a successful call to the /api/weather endpoint with test data."""
    db_session.add(WeatherRecord(station_id="TEST001", date=date(2025, 1, 1)))
    db_session.commit()

    response = client.get("/api/weather")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["station_id"] == "TEST001"


def test_weather_records_pagination(db_session):
    """Tests that the pagination query parameter (page_size) works correctly."""
    for i in range(10):
        db_session.add(WeatherRecord(station_id="TEST002", date=date(2025, 1, i + 1)))
    db_session.commit()

    response = client.get("/api/weather?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_weather_records_filter_by_station(db_session):
    """Tests filtering weather records by station_id."""
    db_session.add(WeatherRecord(station_id="STATION_A", date=date(2025, 1, 1)))
    db_session.add(WeatherRecord(station_id="STATION_B", date=date(2025, 1, 1)))
    db_session.commit()
    
    response = client.get("/api/weather?station_id=STATION_A")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["station_id"] == "STATION_A"


def test_get_weather_stats_success(db_session):
    """Tests a successful call to the /api/weather/stats endpoint."""
    db_session.add(WeatherStatistics(station_id="TEST003", year=1995))
    db_session.commit()

    response = client.get("/api/weather/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["year"] == 1995


def test_weather_stats_filter_by_year(db_session):
    """Tests that filtering the statistics by year works correctly."""
    db_session.add(WeatherStatistics(station_id="TEST004", year=1995))
    db_session.add(WeatherStatistics(station_id="TEST004", year=2005))
    db_session.commit()

    response = client.get("/api/weather/stats?year=1995")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["year"] == 1995
