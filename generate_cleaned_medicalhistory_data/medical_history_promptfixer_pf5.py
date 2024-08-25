import os
from tqdm import tqdm

INPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\input'

OLD_STRING = r'''required\": [\n          \"PatientID\",\n          \"VisitDate\",\n          \"VisitType\",\n          \"MedicalNotes\"\n        ]'''

NEW_STRING = r'''required\": [\n          \"PatientID\",\n          \"VisitDate\",\n          \"VisitType\",\n          \"BloodPressure\",\n          \"Pulse\",\n          \"SpO2\",\n          \"Temperature\",\n          \"Weight\",\n          \"Height\",\n          \"Symptoms\",\n          \"Diagnosis\",\n          \"MedicationPrescribed\",\n          \"LabResults\",\n          \"Procedures\",\n          \"MedicalNotes\"\n        ]'''

def replace_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = content.replace(OLD_STRING, NEW_STRING)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        return True
    return False

def main():
    jsonl_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jsonl')]
    files_updated = 0
    total_replacements = 0

    for file in tqdm(jsonl_files, desc="Updating files"):
        file_path = os.path.join(INPUT_DIR, file)
        if replace_in_file(file_path):
            files_updated += 1
            with open(file_path, 'r', encoding='utf-8') as f:
                total_replacements += f.read().count(NEW_STRING)

    print(f"Updated {files_updated} out of {len(jsonl_files)} files.")
    print(f"Total replacements made: {total_replacements}")

if __name__ == "__main__":
    main()