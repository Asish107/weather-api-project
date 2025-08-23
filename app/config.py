# app/config.py

"""
Centralized configuration settings for the application.
"""
import os  # Import the os module
from pathlib import Path

# Define the project's base directory for reliable path construction.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the database and data directory paths.
# Use os.getenv to read from an environment variable, with a default value.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'weather.db'}")
DATA_DIR = BASE_DIR / "wx_data"