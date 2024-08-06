# Shaswato Sarker - TrustedAI


import os
import json
import csv
import glob
import re
from datetime import datetime

# Base directories
INPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\output'
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\formatted'
COMPLETE_DIR = os.path.join(OUTPUT_DIR, 'complete')
TRACKING_FILE = os.path.join(OUTPUT_DIR, 'format_tracking_log.json')

def ensure_directories():
    for directory in [OUTPUT_DIR, COMPLETE_DIR]:
        os.makedirs(directory, exist_ok=True)

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        return [json.loads(line) for line in f]

def extract_patient_info(content):
    patient_info_pattern = r'(Patient (?:Information|Profile|Summary):[\s\S]*?)(?=\n\n|\Z)'
    matches = list(re.finditer(patient_info_pattern, content))
    
    if matches:
        info_section = matches[-1].group(1)
    else:
        return {}
    
    info_dict = {}
    for line in info_section.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            info_dict[key.strip('- ').strip()] = value.strip()
    
    return info_dict

def parse_batch_prompt(file_path):
    data = {}
    batch_prompts = load_jsonl(file_path)
    for prompt in batch_prompts:
        custom_id = prompt['custom_id']
        messages = prompt['body']['messages']
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        
        if user_messages:
            patient_info = extract_patient_info(user_messages[-1]['content'])
            data[custom_id] = {
                'Name': patient_info.get('Name', ''),
                'Personal Identity Code': patient_info.get('Personal Identity Code', ''),
                'Age': patient_info.get('Age', ''),
                'Address': patient_info.get('Address', ''),
                'Condition': patient_info.get('Condition', '')
            }
    return data

def parse_results(file_path):
    data = {}
    results = load_jsonl(file_path)
    for result in results:
        custom_id = result['custom_id']
        report = result['response']['body']['choices'][0]['message']['content']
        data[custom_id] = {'Report': report}
    return data

def combine_data(batch_data, results_data):
    combined = []
    for custom_id, batch_info in batch_data.items():
        if custom_id in results_data:
            combined.append({**batch_info, **results_data[custom_id]})
    return combined

def write_csv(data, filename, directory):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return file_path

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tracking(tracking):
    with open(TRACKING_FILE, 'w') as f:
        json.dump(tracking, f, indent=2)

def process_directory(subdir, tracking):
    batch_prompt_file = glob.glob(os.path.join(subdir, 'batch_prompts_*.jsonl'))
    results_file = glob.glob(os.path.join(subdir, 'results_*.jsonl'))

    if not (batch_prompt_file and results_file):
        print(f"Incomplete files in {subdir}. Skipping.")
        return tracking

    batch_prompt_file = batch_prompt_file[0]
    results_file = results_file[0]

    # Check if already processed
    if subdir in tracking and tracking[subdir]['status'] == 'success':
        print(f"Already processed {subdir}. Skipping.")
        return tracking

    try:
        # Parse files
        batch_data = parse_batch_prompt(batch_prompt_file)
        results_data = parse_results(results_file)

        # Combine data
        combined_data = combine_data(batch_data, results_data)

        if not combined_data:
            raise ValueError("No data to write")

        # Write combined CSV
        batch_name = os.path.basename(batch_prompt_file).split('.')[0]
        csv_filename = f"dataset_{batch_name}.csv"
        write_csv(combined_data, csv_filename, COMPLETE_DIR)
        write_csv(combined_data, csv_filename, subdir)

        # Update tracking
        tracking[subdir] = {
            'status': 'success',
            'processed_at': datetime.now().isoformat(),
            'rows_completed': len(combined_data)
        }
        print(f"Processed {batch_name}: {len(combined_data)} rows")
    except Exception as e:
        tracking[subdir] = {
            'status': 'failed',
            'processed_at': datetime.now().isoformat(),
            'error': str(e)
        }
        print(f"Failed to process {subdir}: {str(e)}")

    return tracking

def main():
    ensure_directories()
    tracking = load_tracking()
    
    for subdir in glob.glob(os.path.join(INPUT_DIR, 'sub_*')):
        print(f"Processing {subdir}")
        tracking = process_directory(subdir, tracking)
        save_tracking(tracking)

    print("All directories processed.")

if __name__ == "__main__":
    main()