import os
import json
import csv
import re
import jsonlines
from datetime import datetime
import argparse
import shutil
from json_repair import repair_json

# Base directories
INPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\output'
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\formatted\complete'
ERROR_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\formatted\errors'
ERROR_LOG_FILE = os.path.join(OUTPUT_DIR, 'error_log.txt')
TRACKING_FILE = os.path.join(OUTPUT_DIR, 'format_tracking_log.json')

# Ensure output and error directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)

# Set the maximum number of patients to process
MAX_PATIENTS = None  # Change this value to set the limit

# Toggle for format file tracking
ENABLE_TRACKING = True

def log_error(message):
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8-sig') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"{datetime.now().isoformat()}\n")
        f.write(message)
        f.write(f"\n{'='*50}\n")

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tracking(tracking):
    temp_file = TRACKING_FILE + '.temp'
    with open(temp_file, 'w') as f:
        json.dump(tracking, f, indent=2)
    os.replace(temp_file, TRACKING_FILE)

def get_unprocessed_files(all_results_files, tracking):
    return [file for file in all_results_files 
            if os.path.basename(file) not in tracking or not tracking[os.path.basename(file)]["processed"]]


def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'\s+', ' ', text).strip()
    return text

def parse_lab_results(lab_results):
    if isinstance(lab_results, dict):
        return lab_results, None  # Return the dictionary as is, with no additional visit

    lab_results = clean_text(lab_results)
    current_visit = {}
    additional_visit = None

    # Extract main lab results
    main_lab_pattern = r'^(.*?)(?=PatientID:|$)'
    main_lab_match = re.search(main_lab_pattern, lab_results, re.DOTALL)
    if main_lab_match:
        current_visit['LabResults'] = clean_text(main_lab_match.group(1))

    # Extract procedures and medical notes from main lab results
    procedures_pattern = r"Procedures:\s*([^;]+)"
    medical_notes_pattern = r"MedicalNotes:\s*([^;]+)"
    
    procedures_match = re.search(procedures_pattern, current_visit.get('LabResults', ''))
    if procedures_match:
        current_visit['Procedures'] = clean_text(procedures_match.group(1))
        current_visit['LabResults'] = re.sub(procedures_pattern, '', current_visit['LabResults'])

    medical_notes_match = re.search(medical_notes_pattern, current_visit.get('LabResults', ''))
    if medical_notes_match:
        current_visit['MedicalNotes'] = clean_text(medical_notes_match.group(1))
        current_visit['LabResults'] = re.sub(medical_notes_pattern, '', current_visit['LabResults'])

    # Clean up remaining lab results
    current_visit['LabResults'] = re.sub(r"[{}']", "", current_visit['LabResults'])
    current_visit['LabResults'] = clean_text(current_visit['LabResults'])

    # Extract additional visit
    additional_visit_pattern = r'PatientID:\s*([^;]+).*?VisitDate:\s*([^;]+).*?VisitType:\s*([^;]+).*?BloodPressure:\s*([^;]+).*?Pulse:\s*([^;]+).*?SpO2:\s*([^;]+).*?Temperature:\s*([^;]+).*?Weight:\s*([^;]+).*?Height:\s*([^;]+).*?Symptoms:\s*([^;]+).*?Diagnosis:\s*([^;]+).*?MedicationPrescribed:\s*([^;]+)'
    additional_visit_match = re.search(additional_visit_pattern, lab_results, re.DOTALL)
    
    if additional_visit_match:
        additional_visit = {
            'PatientID': additional_visit_match.group(1).strip(),
            'VisitDate': additional_visit_match.group(2).strip(),
            'VisitType': additional_visit_match.group(3).strip(),
            'BloodPressure': additional_visit_match.group(4).strip(),
            'Pulse': additional_visit_match.group(5).strip(),
            'SpO2': additional_visit_match.group(6).strip(),
            'Temperature': additional_visit_match.group(7).strip(),
            'Weight': additional_visit_match.group(8).strip(),
            'Height': additional_visit_match.group(9).strip(),
            'Symptoms': additional_visit_match.group(10).strip(),
            'Diagnosis': additional_visit_match.group(11).strip(),
            'MedicationPrescribed': additional_visit_match.group(12).strip(),
        }
        
        # Extract LabResults for additional visit
        lab_results_pattern = r'LabResults:\s*(.+?)(?=\s*$)'
        lab_results_match = re.search(lab_results_pattern, lab_results, re.DOTALL)
        if lab_results_match:
            additional_visit_lab_results = lab_results_match.group(1).strip()
            additional_visit_parsed, _ = parse_lab_results(additional_visit_lab_results)
            additional_visit.update(additional_visit_parsed)

    return current_visit, additional_visit
def process_visit(visit):
    if isinstance(visit, str):
        # If visit is a string, try to parse it as JSON
        try:
            visit = json.loads(repair_json(visit))
        except json.JSONDecodeError:
            # If parsing fails, return the string as is
            return visit, None

    processed_visit = visit.copy() if isinstance(visit, dict) else {}
    
    if 'LabResults' in processed_visit:
        if isinstance(processed_visit['LabResults'], str):
            current_visit, additional_visit = parse_lab_results(processed_visit['LabResults'])
            
            # Update current visit
            for key, value in current_visit.items():
                if key in processed_visit and processed_visit[key]:
                    if key == 'LabResults':
                        processed_visit[key] = value
                else:
                    processed_visit[key] = value
            
            # Return additional visit if found
            return processed_visit, additional_visit
        elif isinstance(processed_visit['LabResults'], dict):
            # If LabResults is already a dictionary, return it as is
            return processed_visit, None
        else:
            # If LabResults is neither string nor dict, convert to string
            processed_visit['LabResults'] = str(processed_visit['LabResults'])
            return processed_visit, None
    
    return processed_visit, None

def separate_visits(content):
    try:
        if content is None:
            raise ValueError("Content is None")
        
        if isinstance(content, str):
            json_data = json.loads(repair_json(content))
        elif isinstance(content, dict):
            json_data = content
        else:
            raise ValueError(f"Unexpected content type: {type(content)}")
        
        visits = json_data.get('Visits', [])
        processed_visits = []
        
        for visit in visits:
            processed_visit, additional_visit = process_visit(visit)
            processed_visits.append(processed_visit)
            if additional_visit:
                processed_visits.append(additional_visit)
        
        return json_data, processed_visits
    except json.JSONDecodeError as e:
        log_error(f"JSON Decode Error: {str(e)}")
        return None, []
    except ValueError as e:
        log_error(f"Value Error: {str(e)}")
        return None, []

def json_to_csv(json_data, visits):
    csv_data = []
    column_order = [
        'PatientID', 'Name', 'DateOfBirth', 'Gender', 'Address', 'InitialCondition',
        'LongTermConditions', 'SecondaryConditions', 'Allergies', 'MedicationHistory',
        'VisitDate', 'VisitType', 'BloodPressure', 'Pulse', 'SpO2', 'Temperature',
        'Weight', 'Height', 'Symptoms', 'Diagnosis', 'MedicationPrescribed',
        'LabResults', 'Procedures', 'MedicalNotes'
    ]
    
    patient_info = {key: json_data.get(key, '') for key in column_order[:10]}
    patient_info.update({
        'LongTermConditions': ', '.join(str(x) for x in json_data.get('LongTermConditions', [])) or 'None',
        'SecondaryConditions': ', '.join(str(x) for x in json_data.get('SecondaryConditions', [])) or 'None',
        'Allergies': ', '.join(str(x) for x in json_data.get('Allergies', [])) or 'None',
        'MedicationHistory': '; '.join(str(x) for x in json_data.get('MedicationHistory', [])) or 'None'
    })

    for visit in visits:
        visit_data = patient_info.copy()
        for key in column_order[10:]:
            visit_data[key] = str(visit.get(key, '')) or 'None'
        csv_data.append(visit_data)

    return csv_data, column_order

def save_csv(data, fieldnames, filename):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def copy_error_files(jsonl_file, patient_index, error_message, csv_file=None):
    base_name = os.path.splitext(os.path.basename(jsonl_file))[0]
    error_subdir = os.path.join(ERROR_DIR, f"{base_name}_patient_{patient_index + 1}")
    os.makedirs(error_subdir, exist_ok=True)
    
    shutil.copy2(jsonl_file, os.path.join(error_subdir, os.path.basename(jsonl_file)))
    
    with jsonlines.open(jsonl_file) as reader:
        for i, line in enumerate(reader):
            if i == patient_index:
                with open(os.path.join(error_subdir, f"patient_{patient_index + 1}.json"), 'w', encoding='utf-8') as f:
                    json.dump(line, f, indent=2, ensure_ascii=False)
                break
    
    if csv_file and os.path.exists(csv_file):
        shutil.copy2(csv_file, os.path.join(error_subdir, os.path.basename(csv_file)))
    
    with open(os.path.join(error_subdir, 'error_log.txt'), 'w', encoding='utf-8') as f:
        f.write(f"Error processing patient {patient_index + 1} from {os.path.basename(jsonl_file)}:\n{error_message}")

def process_jsonl_file(file_path, max_patients):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    processed_patients = 0
    
    print(f"Starting to process file: {file_path}")
    print(f"Max patients to process: {max_patients}")
    
    with jsonlines.open(file_path) as reader:
        for i, line in enumerate(reader, 1):
            if max_patients is not None and processed_patients >= max_patients:
                print(f"Reached max patients limit ({max_patients}). Stopping processing.")
                break
            
            output_file = os.path.join(OUTPUT_DIR, f"{base_name}_patient_{i}.csv")
            
            try:
                if 'function_call' in line['response']['body']['choices'][0]['message']:
                    content = line['response']['body']['choices'][0]['message']['function_call']['arguments']
                else:
                    content = line['response']['body']['choices'][0]['message']['content']
                
                if isinstance(content, str):
                    content = content.strip('`').strip()
                    if content.startswith('json'):
                        content = content[4:].strip()
                    content = json.loads(repair_json(content))
                
                # Ensure all required fields are present
                required_fields = ['LongTermConditions', 'SecondaryConditions', 'Allergies', 'MedicationHistory']
                for field in required_fields:
                    if field not in content:
                        content[field] = []
                
                json_data, visits = separate_visits(content)
                if json_data is None:
                    raise ValueError("Failed to parse JSON data")
                
                csv_data, fieldnames = json_to_csv(json_data, visits)
                
                # Apply the correction step
                corrected_csv_data = []
                for row in csv_data:
                    current_visit, additional_visit = parse_lab_results(row['LabResults'])
                    
                    # Update the current row
                    for key, value in current_visit.items():
                        if key in row and row[key]:
                            if key == 'LabResults':
                                row[key] = value
                        else:
                            row[key] = value
                    corrected_csv_data.append(row)
                    
                    # Add additional visit if found
                    if additional_visit:
                        new_row = row.copy()
                        new_row.update(additional_visit)
                        corrected_csv_data.append(new_row)
                
                save_csv(corrected_csv_data, fieldnames, output_file)
                processed_patients += 1
                
            except Exception as e:
                error_message = f"Error processing patient {i} in file {file_path}:\n"
                error_message += f"Error details: {str(e)}\n"
                log_error(error_message)
                print(f"Error processing patient {i} in {file_path}. See error log for details.")
                
                copy_error_files(file_path, i-1, error_message, output_file)
    
    print(f"Finished processing file. Total patients processed: {processed_patients}")
    return processed_patients
def main():
    parser = argparse.ArgumentParser(description='Process medical history JSON files.')
    parser.add_argument('--max_patients', type=int, default=MAX_PATIENTS, help='Maximum number of patients to process. If not specified, use the default MAX_PATIENTS value.')
    args = parser.parse_args()

    max_patients = args.max_patients

    all_results_files = []
    for subdir in os.listdir(INPUT_DIR):
        subdir_path = os.path.join(INPUT_DIR, subdir)
        if os.path.isdir(subdir_path):
            results_file = next((f for f in os.listdir(subdir_path) if f.startswith('results_')), None)
            if results_file:
                all_results_files.append(os.path.join(subdir_path, results_file))

    tracking = load_tracking() if ENABLE_TRACKING else {}
    unprocessed_files = get_unprocessed_files(all_results_files, tracking) if ENABLE_TRACKING else all_results_files

    print(f"Total files to process: {len(unprocessed_files)}")

    patients_processed = 0
    for file in unprocessed_files:
        print(f"Processing file: {file}")
        patients_in_file = sum(1 for _ in jsonlines.open(file))
        print(f"Patients in file: {patients_in_file}")
        
        patients_to_process = min(max_patients - patients_processed, patients_in_file) if max_patients is not None else patients_in_file
        processed = process_jsonl_file(file, patients_to_process)
        patients_processed += processed
        
        print(f"Processed {processed} patients from file {file}")
        
        if ENABLE_TRACKING:
            tracking[os.path.basename(file)] = {"processed": True, "patients": patients_in_file}
            save_tracking(tracking)
        
        if max_patients is not None and patients_processed >= max_patients:
            break

    print(f"Total patients processed: {patients_processed}")

if __name__ == "__main__":
    main()