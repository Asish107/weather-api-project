# app/stats.py

"""
Calculates and stores yearly weather statistics for each station.
This script is idempotent and can be run multiple times.
"""

import logging
from datetime import datetime

from sqlalchemy import create_engine, text

from . import models, config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_and_store_stats():
    """Calculates and upserts yearly weather statistics into the database."""
    engine = create_engine(config.DATABASE_URL)
    models.Base.metadata.create_all(engine)

    logging.info("Starting weather statistics calculation.")
    start_time = datetime.now()

    # This SQL query calculates all statistics and is designed to be idempotent
    # using an "upsert" (ON CONFLICT DO UPDATE).
    upsert_query = text("""
        INSERT INTO weather_statistics (station_id, year, avg_max_temp, avg_min_temp, total_precipitation)
        SELECT
            station_id,
            CAST(strftime('%Y', date) AS INTEGER) AS year,
            AVG(max_temp) / 10.0 AS avg_max_temp,
            AVG(min_temp) / 10.0 AS avg_min_temp,
            SUM(precipitation) / 100.0 AS total_precipitation
        FROM
            weather_records
        WHERE
            max_temp != -9999 AND
            min_temp != -9999 AND
            precipitation != -9999
        GROUP BY
            station_id, year
        ON CONFLICT(station_id, year) DO UPDATE SET
            avg_max_temp = excluded.avg_max_temp,
            avg_min_temp = excluded.avg_min_temp,
            total_precipitation = excluded.total_precipitation;
    """)

    # The 'with' block automatically handles the transaction.
    # It will commit on success or rollback on error.
    with engine.connect() as connection:
        result = connection.execute(upsert_query)
        # The connection.commit() line has been removed as it's not needed here.

    end_time = datetime.now()
    logging.info(f"Finished statistics calculation in {end_time - start_time}.")
    logging.info(f"Processed and stored statistics for {result.rowcount} station-years.")


if __name__ == "__main__":
    calculate_and_store_stats()
