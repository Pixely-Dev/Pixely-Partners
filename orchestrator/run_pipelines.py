import json
import logging
import os
import sys
import argparse # Import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    """Loads the JSON configuration file."""
    logging.info(f"Loading configuration from {config_path}...")
    with open(config_path, 'r') as f:
        return json.load(f)

def run_ingestion_pipeline(module_to_run="all"): # Add module_to_run parameter
    """
    Main entry point: loads config, fetches data from Google Sheets, and saves it locally.
    """
    logging.info("Cron job triggered. Starting the ingestion pipeline...")
    
    base_dir = os.path.dirname(__file__)
    inputs_dir = os.path.join(base_dir, 'inputs')
    outputs_dir = os.path.join(base_dir, 'outputs')
    config_path = os.path.join(inputs_dir, 'config.json')

    # Create outputs directory if it doesn't exist
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    try:
        config = load_config(config_path)
        
        # Add the social media pipeline directory to the Python path
        pipeline_dir = os.path.join(base_dir, 'pipelines', 'social_media')
        if pipeline_dir not in sys.path:
            sys.path.append(pipeline_dir)
        
        from ingest_utils import get_data_from_sheet, get_client_data

        # Check if social_media pipeline is active
        if "social_media" in config.get("active_pipelines", []):
            logging.info("Social Media pipeline is active. Starting data ingestion...")
            
            google_sheet_url = config.get("google_sheet_url")
            if not google_sheet_url:
                raise ValueError("google_sheet_url not found in config.json")

            output_file_path = os.path.join(outputs_dir, 'ingested_data.json')

            if os.path.exists(output_file_path):
                logging.info(f"'{output_file_path}' already exists. Skipping data ingestion and using existing file.")
            else:
                # Fetch all required data from Google Sheets
                fichas_df = get_data_from_sheet(google_sheet_url, config["tabs"]["social_media_fichas_cliente"])
                posts_df = get_data_from_sheet(google_sheet_url, config["tabs"]["social_media_publicaciones"])
                comments_df = get_data_from_sheet(google_sheet_url, config["tabs"]["social_media_comentarios"])

                if fichas_df is None or posts_df is None or comments_df is None:
                    raise Exception("Failed to fetch one or more data tabs from Google Sheets.")

                # Filter data for the specific client
                client_id = config.get("client_id")
                client_ficha = get_client_data(fichas_df, client_id)
                
                if not client_ficha:
                    raise Exception(f"No data found for client_id {client_id} in 'Ficha Cliente' tab.")

                # --- Verification Step ---
                # Save the ingested data to a local JSON file for verification
                output_payload = {
                    "client_ficha": client_ficha,
                    "posts": posts_df[posts_df['client_id'] == client_id].to_dict('records'),
                    "comments": comments_df.to_dict('records') # Assuming comments are linked by post_url
                }
                
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_payload, f, ensure_ascii=False, indent=4)

                logging.info(f"Ingestion successful. Data saved to {output_file_path}")
            
            # Call the analysis module
            logging.info("Executing main analysis function with loaded data...")
            # Ensure the social_media pipeline directory is in sys.path for analyze.py to be found
            from analyze import analyze_data
            import asyncio
            asyncio.run(analyze_data(config=config, module_to_run=module_to_run)) # Pass module_to_run

        else:
            logging.info("Social Media pipeline is not active. Skipping.")

    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Pixely Orchestrator pipelines.")
    parser.add_argument("--module", "-m", type=str, default="all",
                        help="Specify which Qx module to run (e.g., Q1, Q2). Use 'all' to run all active modules.")
    args = parser.parse_args()
    run_ingestion_pipeline(module_to_run=args.module)
