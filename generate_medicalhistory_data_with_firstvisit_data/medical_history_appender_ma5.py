import os
import pandas as pd
import glob
import json
from datetime import datetime
from tqdm import tqdm

# Base directories
COMPLETE_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\files_medhistory\formatted\complete'
APPENDED_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\files_medhistory\formatted\appended'
TRACKING_FILE = os.path.join(APPENDED_DIR, 'append_tracking_log.json')
LOG_FILE = os.path.join(APPENDED_DIR, 'append_log.txt')

# Configuration
APPEND_TRACKING = False  # Set to False to append all files regardless of previous processing

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            data = json.load(f)
            return set([item['processed_patients'] for item in data.values()])
    return set()

def save_tracking(processed_patients):
    data = {i: {"processed_patients": patient} for i, patient in enumerate(processed_patients)}
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp}: {message}\n")

def append_csv_files():
    # Ensure the output directory exists
    os.makedirs(APPENDED_DIR, exist_ok=True)

    # Get all CSV files in the COMPLETE_DIR
    all_csv_files = glob.glob(os.path.join(COMPLETE_DIR, '*.csv'))

    if not all_csv_files:
        print("No CSV files found to process.")
        return

    # Load tracking data
    processed_patients = load_tracking() if APPEND_TRACKING else set()

    # Filter out already processed files
    unprocessed_files = [file for file in all_csv_files if os.path.splitext(os.path.basename(file))[0] not in processed_patients]

    if not unprocessed_files:
        print("No new files to process.")
        return

    print(f"Total files to process: {len(unprocessed_files)}")

    # Create the output file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(APPENDED_DIR, f'appended_{timestamp}.csv')

    # Create progress bar
    pbar = tqdm(total=len(unprocessed_files), desc="Appending CSV files", unit="file")

    # Read and concatenate all CSV files
    dfs = []
    for csv_file in unprocessed_files:
        patient_id = os.path.splitext(os.path.basename(csv_file))[0]
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig', low_memory=False)
            dfs.append(df)
            processed_patients.add(patient_id)
            log_message(f"Appended patient: {patient_id}")
        except Exception as e:
            log_message(f"Error processing file {csv_file}: {str(e)}")
            print(f"Error processing file {csv_file}. See log for details.")
        finally:
            pbar.update(1)

    pbar.close()

    if dfs:
        try:
            # Concatenate all dataframes
            combined_df = pd.concat(dfs, ignore_index=True)

            # Write the combined dataframe to CSV
            combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')

            # Update and save tracking data
            save_tracking(processed_patients)

            print(f"Appended {len(dfs)} patients to {output_file}")
            log_message(f"Appended {len(dfs)} patients to {output_file}")
        except Exception as e:
            error_msg = f"Error while concatenating or saving data: {str(e)}"
            print(error_msg)
            log_message(error_msg)
    else:
        print("No new data to append.")
        log_message("No new data to append.")
        
if __name__ == "__main__":
    append_csv_files()