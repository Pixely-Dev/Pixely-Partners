
import pandas as pd
import numpy as np
import logging
import sys
import os
import json
from datetime import datetime, timedelta

# Add the pipeline directory to the Python path to import ingest_utils
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from ingest_utils import get_google_sheets_client
import gspread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """Loads the main JSON configuration file."""
    # Go up two levels from social_media -> pipelines -> orchestrator
    orchestrator_dir = os.path.dirname(os.path.dirname(base_dir))
    config_path = os.path.join(orchestrator_dir, 'inputs', 'config.json')
    logging.info(f"Loading configuration from {config_path}...")
    with open(config_path, 'r') as f:
        return json.load(f)

def generate_test_data(client_id, client_name):
    """Generates structured test data as pandas DataFrames."""
    logging.info("Generating test data...")

    # --- Ficha Cliente ---
    ficha_data = {
        'client_id': [client_id],
        'client_name': [client_name],
        'primary_business_goal': ['Brand Awareness'],
        'competitor_1': ['Adidas'], 'competitor_2': ['Puma'], 'competitor_3': ['Reebok'], 'competitor_4': ['Under Armour'],
        'seguidores_instagram': [150000000], 'seguidores_tiktok': [5000000], 'seguidores_facebook': [100000000]
    }
    ficha_df = pd.DataFrame(ficha_data)

    # --- Social Media Posts ---
    posts_data = {
        'client_id': [client_id] * 5,
        'post_url': [
            'https://www.instagram.com/p/Cxyz123', 
            'https://www.instagram.com/p/Abcd456', 
            'https://www.tiktok.com/v/12345', 
            'https://www.facebook.com/photo/78910', 
            'https://www.instagram.com/p/Efgh789'
        ],
        'platform': ['instagram', 'instagram', 'tiktok', 'facebook', 'instagram'],
        'likes': np.random.randint(10000, 500000, size=5),
        'comments': np.random.randint(100, 5000, size=5),
        'views': np.random.randint(100000, 5000000, size=5),
        'shares': np.random.randint(500, 10000, size=5)
    }
    posts_df = pd.DataFrame(posts_data)

    # --- Comentarios ---
    comments_text = [
        "Just do it! Best shoes ever.", "Love the new collection!", "When is the next drop?",
        "These are so comfortable.", "Amazing design.", "Need these in my life.",
        "My favorite brand!", "Great quality as always.", "Can't wait to buy them.",
        "The colorway is sick!", "Instant cop!", "So hyped for this release."
    ]
    comments_data = {
        'post_url': np.random.choice(posts_data['post_url'], size=12),
        'text': comments_text,
        'author': [f'user_{i:03d}' for i in range(12)],
        'timestamp': [(datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat() for _ in range(12)]
    }
    comments_df = pd.DataFrame(comments_data)
    
    logging.info("Test data generated successfully.")
    return {"Ficha Cliente": ficha_df, "Social_Media_Posts": posts_df, "Comentarios": comments_df}

def populate_google_sheet(sheet_url, dataframes):
    """Clears and populates a Google Sheet with the provided DataFrames."""
    logging.info(f"Connecting to Google Sheet: {sheet_url}")
    try:
        client = get_google_sheets_client()
        spreadsheet = client.open_by_url(sheet_url)

        for tab_name, df in dataframes.items():
            logging.info(f"Processing tab: '{tab_name}'...")
            try:
                worksheet = spreadsheet.worksheet(tab_name)
            except gspread.exceptions.WorksheetNotFound:
                logging.warning(f"Tab '{tab_name}' not found. Creating it...")
                worksheet = spreadsheet.add_worksheet(title=tab_name, rows=100, cols=20)

            # Clear the sheet and update with new data
            worksheet.clear()
            header = [df.columns.values.tolist()]
            data = df.values.tolist()
            worksheet.update(header + data, range_name='A1')
            logging.info(f"Tab '{tab_name}' populated successfully with {len(df)} rows.")

        logging.info("Google Sheet population complete.")

    except Exception as e:
        logging.error(f"An error occurred while populating the Google Sheet: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    config = load_config()
    sheet_url = config.get("google_sheet_url")
    client_id = config.get("client_id")
    client_name = config.get("client_name")

    if not all([sheet_url, client_id, client_name]):
        logging.error("Configuration is missing 'google_sheet_url', 'client_id', or 'client_name'.")
        sys.exit(1)

    # Generate and populate
    test_dataframes = generate_test_data(client_id, client_name)
    populate_google_sheet(sheet_url, test_dataframes)
