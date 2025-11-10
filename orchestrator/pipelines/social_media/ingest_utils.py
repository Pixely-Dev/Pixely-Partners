
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_google_sheets_client():
    """Authenticates with Google Sheets API using service account credentials."""
    logging.info("Authenticating with Google Sheets API...")
    
    # Path to the credentials file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    credentials_path = os.path.join(base_dir, 'gcp_credentials.json')

    if not os.path.exists(credentials_path):
        logging.error(f"Credentials file not found at {credentials_path}")
        raise FileNotFoundError(f"Credentials file not found at {credentials_path}")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(creds)
    
    logging.info("Google Sheets API authentication successful.")
    return client

def get_data_from_sheet(google_sheet_url, tab_name):
    """Fetches data from a specific tab of a Google Sheet and returns it as a DataFrame."""
    try:
        client = get_google_sheets_client()
        spreadsheet = client.open_by_url(google_sheet_url)
        worksheet = spreadsheet.worksheet(tab_name)
        
        logging.info(f"Fetching data from tab: {tab_name}...")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        logging.info(f"Successfully fetched {len(df)} rows from {tab_name}.")
        return df

    except gspread.exceptions.WorksheetNotFound:
        logging.error(f"Tab (Worksheet) '{tab_name}' not found in the Google Sheet.")
        return None
    except Exception as e:
        logging.error(f"An error occurred while fetching data from Google Sheets: {e}", exc_info=True)
        return None

def get_client_data(df, client_id):
    """Filters the client data DataFrame for a specific client_id."""
    if 'client_id' not in df.columns:
        logging.error("'client_id' column not found in the DataFrame.")
        return None
    
    client_data = df[df['client_id'] == client_id].to_dict('records')
    
    if not client_data:
        logging.warning(f"No data found for client_id: {client_id}")
        return None
        
    logging.info(f"Found data for client_id: {client_id}.")
    return client_data[0]

# Placeholder for future API authentication logic
def login_orchestrator(api_url, username, password):
    """
    (DISABLED) Authenticates the orchestrator with the API to get a JWT token.
    """
    logging.info("API authentication is currently disabled.")
    # In the future, this function will make a POST request to the API's /token endpoint
    # and return the access token.
    return "fake-jwt-token-for-development"

