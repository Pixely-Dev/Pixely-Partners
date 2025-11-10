import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from database import Base, engine
from models import *

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

if __name__ == "__main__":
    for i in range(MAX_RETRIES):
        try:
            print(f"Attempting to connect to database (attempt {i + 1}/{MAX_RETRIES})...")
            # Try to create tables
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
            break
        except OperationalError as e:
            print(f"Database connection failed: {e}")
            if i < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Could not connect to the database.")
                exit(1)