import os
import json
import random
from faker import Faker
from datetime import datetime
import csv
import tiktoken
import uuid
from tqdm import tqdm
import pandas as pd
from collections import deque
import outlines
from outlines import models
import outlines.models.openai
import traceback

# Base directories
INPUT_FILE = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\dataset_appended_20240802_224715.csv' # first visits output csv file
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\input'
DATA_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\data'
LOG_FILE = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files_medhistory\processed_patients.json'

fake = Faker('fi_FI')  # Finnish locale

def load_examples():
    examples_file = os.path.join(DATA_DIR, 'medical_history_examples.json')
    with open(examples_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_processed_patients():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_patients(processed):
    with open(LOG_FILE, 'w') as f:
        json.dump(list(processed), f)

def load_patients():
    return pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

def create_patient_id(dob, initials):
    dob_parts = dob.split('-')
    if len(dob_parts) == 3:
        return f"{dob_parts[0][2:]}{dob_parts[1]}{dob_parts[2]}{initials.upper()}"
    else:
        return f"{uuid.uuid4().hex[:8]}{initials.upper()}"

def create_json_schema():
    return {
        "type": "object",
        "properties": {
            "PatientID": {"type": "string"},
            "Name": {"type": "string"},
            "DateOfBirth": {"type": "string", "pattern": "^\\d{1,2}/\\d{1,2}/\\d{4}$"},
            "Gender": {"type": "string"},
            "Address": {"type": "string"},
            "InitialCondition": {"type": "string"},
            "LongTermConditions": {"type": "array", "items": {"type": "string"}},
            "SecondaryConditions": {"type": "array", "items": {"type": "string"}},
            "Allergies": {"type": "array", "items": {"type": "string"}},
            "MedicationHistory": {"type": "array", "items": {"type": "string"}},
            "Visits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "PatientID": {"type": "string"},
                        "VisitDate": {"type": "string", "pattern": "^\\d{1,2}/\\d{1,2}/\\d{4}$"},
                        "VisitType": {"type": "string"},
                        "BloodPressure": {"type": "string"},
                        "Pulse": {"type": "number"},
                        "SpO2": {"type": "string"},
                        "Temperature": {"type": "number"},
                        "Weight": {"type": "number"},
                        "Height": {"type": "number"},
                        "Symptoms": {"type": "string"},
                        "Diagnosis": {"type": "string"},
                        "MedicationPrescribed": {"type": "string"},
                        "LabResults": {"type": "string"},
                        "Procedures": {"type": "string"},
                        "MedicalNotes": {"type": "string"}
                    },
                    "required": ["PatientID", "VisitDate", "VisitType", "BloodPressure", "Pulse", "SpO2", "Temperature", "Weight", "Height", "Symptoms", "Diagnosis", "MedicationPrescribed", "LabResults", "Procedures", "MedicalNotes"]
                }
            }
        },
        "required": ["PatientID", "Name", "DateOfBirth", "Gender", "Address", "InitialCondition", "LongTermConditions", "SecondaryConditions", "Allergies", "MedicationHistory", "Visits"]
    }


def create_prompt(patient, examples):
    selected_examples = random.sample(examples, 2)
    example_histories = "\n\n".join([f"Example Medical History:\n{json.dumps(ex, indent=2)}" for ex in selected_examples])
    
    dob = patient.get('DateOfBirth', '')
    initials = ''.join([name[0] for name in patient['Name'].split() if name])
    patient_id = create_patient_id(dob, initials)
    
    json_schema = create_json_schema()
    
    prompt = f"""Generate a comprehensive and realistic medical history for the following patient over the past 2-5 years:

PatientID: {patient_id}
Name: {patient['Name']}
Personal Identity Code: {patient['Personal Identity Code']}
Age: {patient['Age']}
Address: {patient['Address']}
Initial Complaint: {patient.get('InitialCondition', 'Unknown')}

Initial Medical Report:
{patient.get('MedicalNotes', 'No initial report available.')}

Please follow these guidelines:
1. Generate a complete patient profile including PatientID, Name, DateOfBirth, Gender, and Address.
2. Generate [5-25] medical visit records for this patient. Keep max token limit in mind. 
3. Include a mix of visit types: initial consultation, inpatient visit, follow-up, routine check-up, emergency visit, outpatient visit, screening and diagnosis, immunization, pre- and post-operative care, psychiatric visit, telehealth consultation, rehabilitative visit, geriatric visit, and specialist consultation.
4. The InitialCondition should be the presenting complaint or symptom for the first visit, which may or may not develop into a long-term condition.
5. LongTermConditions should only be added if the patient develops a chronic illness (e.g., diabetes, heart disease) that persists for years or life. This may or may not be related to the InitialCondition.
6. SecondaryConditions can include both long-term and short-term health issues that are discovered or develop during the patient's medical history. These may be curable or chronic.
7. Show a realistic progression of the patient's health over time, which may include:
   - Resolution of the InitialCondition
   - Development of new acute or chronic conditions
   - Management and potential complications of LongTermConditions
8. Include any allergies the patient may have or develop. These should be relevant to their medical history and treatment, if the patient has any allegries.
9. MedicationHistory is a detailed account of all medications the patient used prior to their first visit, including dosage, duration of use, reason for taking, and the reason for discontinuation if applicable.  
10. MedicationPrescribed should be a comprehensive list of all medications managed during this visit, including new prescriptions, dosage adjustments, discontinuations, and reasons for changes, based on their current conditions and treatment plans.
11. Vary vital signs and lab results realistically between visits, reflecting the patient's changing health status.
12. Each visit should have a detailed 'MedicalNotes' field describing the visit, findings, and plan. These notes should be comprehensive and include:
    - Detailed description of the patient's current state and symptoms
    - Any changes since the last visit
    - Reasoning behind any changes in treatment or medication
    - Specific instructions given to the patient
    - Any concerns or areas to monitor for the future
    - Follow-up plan and next steps
13. Use medically accurate terminology and realistic diagnostic procedures.
14. Ensure consistency in the patient's overall health story while allowing for realistic changes and developments.
15. Format the DateOfBirth as M/D/YYYY (e.g., 3/15/1985). Ensure all dates are valid (such as the date with an invalid day for the month) and not in the future.
16. For all date fields, including VisitDate, use the M/D/YYYY format and ensure dates are valid and not in the future.

The medical history should be relevant to the patient's condition(s) and include appropriate medical history, condition-specific medical test reports and data, procedures & medications, and follow-up instructions.

We offer some example medical histories for your reference. Although you can refer to these examples, create a distinct and realistic report, using the examples only as inspiration. Keep the reports comprehensive while maintaining clarity and relevance.

Example Medical Histories:
{example_histories}

Provide the output in JSON format according to the following schema:
{json.dumps(json_schema, indent=2)}
"""
    return prompt


def get_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
    return len(encoding.encode(text))

def generate_batch_prompts(num_records, all_patients, processed_patients, examples):
    batch_prompts = []
    available_patients = [p for p in all_patients if p['Personal Identity Code'] not in processed_patients]
    
    for _ in range(num_records):
        if not available_patients:
            break
        
        patient = available_patients.pop(0)
        prompt = create_prompt(patient, examples)
        json_schema = create_json_schema()
        
        batch_prompts.append({
            "custom_id": f"history-request-{len(batch_prompts)+1}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini-2024-07-18",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant tasked with generating a comprehensive medical history for a patient based on their initial medical record. You should create a realistic progression of the patient's condition over time, including various types of medical visits and potential complications or additional conditions."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 10000,
                "functions": [
                    {
                        "name": "generate_medical_history",
                        "description": "Generate a comprehensive medical history for a patient",
                        "parameters": json_schema
                    }
                ],
                "function_call": {"name": "generate_medical_history"}
            }
        })
        processed_patients.add(patient['Personal Identity Code'])
    
    return batch_prompts, len(available_patients)

def save_batch_prompts(batch_prompts, output_directory, filename):
    os.makedirs(output_directory, exist_ok=True)
    filepath = os.path.join(output_directory, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for prompt in batch_prompts:
                f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
        print(f"Successfully saved file: {filepath}")
        print(f"File size: {os.path.getsize(filepath)} bytes")
        return True
    except Exception as e:
        print(f"Error saving file {filepath}: {str(e)}")
        print(traceback.format_exc())
        return False

def main():
    # Configuration
    num_files = 1  # Number of files to create
    num_records = 200  # Number of records per file

    # Load all data upfront
    all_patients = load_patients().to_dict('records')
    processed_patients = load_processed_patients()
    examples = load_examples()

    # Create progress bar
    pbar = tqdm(total=num_files, desc="Generating batch prompt files", unit="file")

    files_created = 0
    for i in range(num_files):
        batch_prompts, remaining_patients = generate_batch_prompts(num_records, all_patients, processed_patients, examples)
        
        if not batch_prompts:
            print("No more unprocessed patients available. Stopping file generation.")
            break
        
        # Create a filename with datetime and file number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'history_batch_prompts_{timestamp}_file{i+1}.jsonl'
        
        if save_batch_prompts(batch_prompts, OUTPUT_DIR, filename):
            files_created += 1
            # Update progress bar
            pbar.update(1)

        print(f"Attempted to create file {i+1}/{num_files} with {len(batch_prompts)} records. Remaining unprocessed patients: {remaining_patients}")
        print(f"Files successfully created so far: {files_created}")

    # Close progress bar
    pbar.close()

    # Save updated processed patients
    save_processed_patients(processed_patients)

    print(f"Attempted to create {num_files} files, successfully created {files_created} files, each with up to {num_records} records.")
    print(f"Total patients processed: {len(processed_patients)}")
    print(f"Files in output directory: {len(os.listdir(OUTPUT_DIR))}")

if __name__ == "__main__":
    main()
