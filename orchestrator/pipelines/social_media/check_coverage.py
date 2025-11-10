
import logging
import sys
import os

# Add the pipeline directory to the Python path to import ingest_utils
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from ingest_utils import get_google_sheets_client
import gspread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Define the required structure: {tab_name: [required_columns]}
REQUIRED_STRUCTURE = {
    "Ficha Cliente": ["client_id", "client_name", "primary_business_goal", "competitor_1", "competitor_2", "competitor_3", "competitor_4", "seguidores_instagram", "seguidores_tiktok", "seguidores_facebook"],
    "Social_Media_Posts": ["client_id", "post_url", "platform", "likes", "comments", "views", "shares"],
    "Comentarios": ["post_url", "text", "author", "timestamp"]
}

# Get the Google Sheet URL from the main config file (assuming a similar structure)
# In a real scenario, this might be read from the same config as the main pipeline
# For this script, we'll hardcode it for simplicity, but it should match config.json
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1kGDc9GI1qnnQHk4n2TfbmRhuua-FOno6mTXXO0czmp4/edit?gid=261178786#gid=261178786"

def check_sheet_coverage(sheet_url, required_structure):
    """
    Connects to a Google Sheet and verifies that the required tabs and columns exist.
    """
    logging.info("Starting Google Sheet coverage check...")
    all_ok = True

    try:
        client = get_google_sheets_client()
        spreadsheet = client.open_by_url(sheet_url)
        
        for tab_name, required_columns in required_structure.items():
            logging.info(f"Checking tab: '{tab_name}'...")
            try:
                worksheet = spreadsheet.worksheet(tab_name)
                header = worksheet.row_values(1) # Get header row
                
                missing_columns = [col for col in required_columns if col not in header]
                
                if not missing_columns:
                    logging.info(f"[SUCCESS] Tab '{tab_name}' has all required columns.")
                else:
                    logging.error(f"[FAILURE] Tab '{tab_name}' is missing columns: {missing_columns}")
                    all_ok = False

            except gspread.exceptions.WorksheetNotFound:
                logging.error(f"[FAILURE] Tab '{tab_name}' not found in the Google Sheet.")
                all_ok = False
            except Exception as e:
                logging.error(f"An unexpected error occurred while checking tab '{tab_name}': {e}")
                all_ok = False

    except Exception as e:
        logging.error(f"Failed to connect to Google Sheets or open the spreadsheet: {e}", exc_info=True)
        all_ok = False

    if all_ok:
        logging.info("\nCoverage Check Passed: The Google Sheet structure is valid.")
    else:
        logging.error("\nCoverage Check Failed: The Google Sheet is missing required tabs or columns.")
        sys.exit(1)

if __name__ == "__main__":
    check_sheet_coverage(GOOGLE_SHEET_URL, REQUIRED_STRUCTURE)
