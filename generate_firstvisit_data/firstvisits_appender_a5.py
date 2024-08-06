# Shaswato Sarker - TrustedAI


import os
import csv
import glob
import json
from datetime import datetime

# Base directories
COMPLETE_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\formatted\complete'
APPENDED_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\formatted\appended'
TRACKING_FILE = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\formatted\append_tracking_log.json'

# Ensure required directories exist
os.makedirs(APPENDED_DIR, exist_ok=True)

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {'processed_files': []}

def save_tracking(tracking):
    with open(TRACKING_FILE, 'w') as f:
        json.dump(tracking, f, indent=2)

def append_csv_files():
    tracking = load_tracking()
    processed_files = set(tracking['processed_files'])
    
    # Get all CSV files in the COMPLETE_DIR
    all_csv_files = glob.glob(os.path.join(COMPLETE_DIR, '*.csv'))
    
    # Filter out already processed files
    new_csv_files = [f for f in all_csv_files if f not in processed_files]
    
    if not new_csv_files:
        print("No new CSV files to process.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(APPENDED_DIR, f'dataset_appended_{timestamp}.csv')
    
    # Write the header only once
    header_written = False
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
        writer = None
        
        for csv_file in new_csv_files:
            with open(csv_file, 'r', encoding='utf-8-sig') as infile:
                reader = csv.reader(infile)
                if not header_written:
                    header = next(reader)
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                    header_written = True
                else:
                    next(reader)  # Skip header for subsequent files
                
                for row in reader:
                    writer.writerow(row)
            
            # Add the processed file to tracking
            processed_files.add(csv_file)
    
    # Update and save tracking information
    tracking['processed_files'] = list(processed_files)
    save_tracking(tracking)
    
    print(f"Appended {len(new_csv_files)} new CSV files to {output_file}")

if __name__ == "__main__":
    append_csv_files()