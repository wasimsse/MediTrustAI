import pandas as pd
import json

# Path to your dataset.csv
csv_file_path = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\misc\dataset.csv'
output_jsonl_path = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\misc\output_dataset.jsonl'

# Load the dataset (try 'utf-8' if 'ISO-8859-1' doesn't handle Finnish characters properly)
df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

# Sort the dataset by PatientID and VisitDate to maintain the chronological order of visits
df = df.sort_values(by=['PatientID', 'VisitDate'])

# Calculate the visit count for each patient
df['VisitCount'] = df.groupby('PatientID').cumcount() + 1

# Function to create a natural language prompt
def create_natural_language_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    # Handle fields that may contain "none", "None Reported", or "None at this time"
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no medications prescribed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures performed" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"The following procedures were performed: {row['Procedures'].lower()}."

    # Remove any double periods or trailing punctuation issues
    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    # Create the user message for the current visit
    user_message = (
        f"This is the {visit_count_str} visit for patient {row['Name']} (ID: {row['PatientID']}), a {row['Age']}-year-old {row['Gender']} "
        f"from {row['Address']}. The patient has a history of {row['InitialCondition']}. In addition, they have been diagnosed with "
        f"the following long-term conditions: {row['LongTermConditions'].lower()} and secondary conditions including {row['SecondaryConditions'].lower()}. "
        f"The patient has {allergies_str}. "
        f"During this visit on {row['VisitDate']}, which is a {row['VisitType']}, they reported the following symptoms: {symptoms_str} "
        f"Vital signs recorded were: blood pressure {row['BloodPressure']}, pulse {row['Pulse']} bpm, oxygen saturation (SpO2) at {row['SpO2']}, "
        f"body temperature at {row['Temperature']}°C, weight {row['Weight']} kg, and height {row['Height']} cm. "
        f"The diagnosis for this visit is {row['Diagnosis'].lower()}. The patient has been {medication_str}. "
        f"Lab results indicate {lab_results_str} {procedures_str}"
    )
    
    # Include relevant previous visit's information if available
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f" During the last visit on {previous_visit_date}, the patient reported {previous_symptoms} "
            f"The diagnosis at that time was {previous_diagnosis}. They were {previous_medication}, "
            f"and lab results showed {previous_lab_results} The medical note from that visit was: {previous_medical_notes}."
        )
    
    # Ensure there is no double punctuation and fix trailing spaces
    user_message = user_message.replace('..', '.').strip()
    
    return {
        "role": "user",
        "content": user_message
    }

# Prepare the JSONL entries
jsonl_entries = []
previous_visit_info = None

for idx, row in df.iterrows():
    user_message = create_natural_language_prompt(row, previous_visit_info)
    assistant_message = {
        "role": "assistant",
        "content": row['MedicalNotes'].rstrip('.').strip() + "."
    }
    jsonl_entry = {
        "messages": [user_message, assistant_message]
    }
    jsonl_entries.append(jsonl_entry)
    
    # Update previous_visit_info to the current row for the next iteration
    previous_visit_info = row

# Write the JSONL entries to a file
with open(output_jsonl_path, 'w') as f:
    for entry in jsonl_entries:
        f.write(json.dumps(entry) + '\n')

print(f"JSONL dataset created at: {output_jsonl_path}")
