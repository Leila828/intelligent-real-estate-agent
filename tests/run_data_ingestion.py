# your_real_estate_project/run_data_ingestion.py

import os
import sys
import pandas as pd
from flask import Flask  # Import Flask to create a dummy app instance

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Import your database and API functions
from database import database
from api import bayut_scraper
from config import DATABASE


def run_ingestion():
    # Create a minimal Flask app instance just for managing the app context
    # This app won't be serving HTTP requests, it's just for context.
    app = Flask(__name__)
    app.config['DATABASE'] = DATABASE  # Configure the database path

    # Register database initialization (schema loading) with this dummy app
    database.init_app(app)

    # Push an application context manually
    # This makes current_app and g available to database functions
    with app.app_context():
        try:
            # 1. Initialize the Database (this will create tables if they don't exist)
            print("\n--- Initializing Database ---")
            # The init_db function from your database.py will now correctly use current_app.open_resource
            database.init_db()

            # 2. Fetch Property Data
            print("\n--- Starting Data Fetching from Bayut API ---")
            raw_fetched_properties = bayut_scraper.get_bayut_property_data(
                purposes=["for-sale", "for-rent"],  # Fetch both for sale and rent
                location_query="",  # All UAE
                property_types=[],  # All types
                max_pages_to_fetch=5,  # Limit initial auto-fetch to a few pages to get started quickly
                delay_seconds=0.2
            )

            if not raw_fetched_properties:
                print("No properties fetched from API. Exiting data ingestion.")
                return

            # 3. Process and Insert into Database
            print("\n--- Inserting Fetched Data into Normalized Database Tables ---")
            properties_inserted_count = 0
            for i, prop_dict in enumerate(raw_fetched_properties):
                # insert_property_normalized expects the raw API dict.
                if database.insert_property_normalized(prop_dict):
                    properties_inserted_count += 1
                if (i + 1) % 100 == 0:
                    print(
                        f"  Processed {i + 1} of {len(raw_fetched_properties)} properties. Inserted/updated: {properties_inserted_count}")

            print(f"\nTotal properties collected from API: {len(raw_fetched_properties)}")
            print(f"Total properties inserted/updated in DB: {properties_inserted_count}")
            print(f"Current total properties in DB: {database.get_all_properties_count()}")

        except Exception as e:
            print(f"An error occurred during data ingestion: {e}")
        finally:
            # The app_context() context manager will handle closing the DB connection
            # via app.teardown_appcontext automatically when it exits.
            print("Data ingestion process finished.")


if __name__ == "__main__":
    run_ingestion()