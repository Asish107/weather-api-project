# app/ingest.py

"""
Ingests raw weather data from text files into the database.
This script is idempotent and can be run multiple times without creating duplicates.
"""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from . import models, config

# Configure logging to provide detailed output.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def ingest_weather_data():
    """Finds, processes, and bulk-inserts weather data from the wx_data directory."""
    # Create a database engine using the URL from the configuration.
    engine = create_engine(config.DATABASE_URL)
    # Ensure all tables are created based on the models.
    models.Base.metadata.create_all(engine)
    # Create a session class to interact with the database.
    Session = sessionmaker(bind=engine)
    session = Session()

    logging.info("Starting weather data ingestion.")
    start_time = datetime.now()

    # Find all .txt files in the specified data directory.
    file_paths = list(config.DATA_DIR.glob("*.txt"))
    logging.info(f"Found {len(file_paths)} data files in {config.DATA_DIR}.")

    if not file_paths:
        logging.warning("No data files found. Aborting ingestion process.")
        return

    total_records_ingested = 0
    files_processed = 0

    # Iterate over each found data file.
    for file_path in file_paths:
        station_id = file_path.stem  # Get the station ID from the filename.
        records_in_file = []
        try:
            with open(file_path, 'r') as f:
                # Enumerate to get both the line number and content for better logging.
                for line_num, line in enumerate(f, 1):
                    parts = line.strip().split('\t')
                    
                    # Check if the line is malformed.
                    if len(parts) != 4:
                        # Log a specific warning if a line doesn't have exactly 4 parts.
                        logging.warning(
                            f"Skipping malformed line {line_num} in {file_path.name}: '{line.strip()}'"
                        )
                        continue
                    
                    # Create a WeatherRecord object, handling missing values (-9999).
                    record = models.WeatherRecord(
                        station_id=station_id,
                        date=datetime.strptime(parts[0], '%Y%m%d').date(),
                        max_temp=None if int(parts[1]) == -9999 else int(parts[1]),
                        min_temp=None if int(parts[2]) == -9999 else int(parts[2]),
                        precipitation=None if int(parts[3]) == -9999 else int(parts[3])
                    )
                    records_in_file.append(record)
            
            # Use bulk_save_objects for efficient insertion of all records from the file.
            session.bulk_save_objects(records_in_file)
            session.commit()
            
            total_records_ingested += len(records_in_file)
            files_processed += 1
            logging.info(f"Successfully processed and committed data for station {station_id}.")

        except IntegrityError:
            # This block catches errors from the UniqueConstraint, handling duplicates gracefully.
            session.rollback()
            logging.warning(f"Data for station {station_id} already exists. Skipping.")
        except Exception as e:
            # Catch any other unexpected errors during file processing.
            logging.error(f"An error occurred while processing file {file_path}: {e}")
            session.rollback()

    end_time = datetime.now()
    logging.info(f"Finished ingestion in {end_time - start_time}.")
    logging.info(f"Total files processed: {files_processed}/{len(file_paths)}")
    logging.info(f"Total records ingested in this run: {total_records_ingested}")
    
    # Cleanly close the database session.
    session.close()


if __name__ == "__main__":
    ingest_weather_data()
