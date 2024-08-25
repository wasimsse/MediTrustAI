import pandas as pd
import json
import chardet
from natural_language_examples_nle2 import create_natural_language_prompt

# Path to your dataset.csv
csv_file_path = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\misc\cleaned_medication_history_appended_20240731_221209.csv'
output_jsonl_path = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\misc\output_dataset.jsonl'

# Detect file encoding
with open(csv_file_path, 'rb') as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)
    file_encoding = result['encoding']

print(f"Detected file encoding: {file_encoding}")

# Load the dataset
df = pd.read_csv(csv_file_path, encoding=file_encoding)

# Sort the dataset by PatientID and VisitDate to maintain the chronological order of visits
df = df.sort_values(by=['PatientID', 'VisitDate'])

# Calculate the visit count for each patient
df['VisitCount'] = df.groupby('PatientID').cumcount() + 1

print(f"Total rows in DataFrame: {len(df)}")

# Function to process a batch of rows
def process_batch(batch, previous_visit_info):
    jsonl_entries = []
    for idx, row in batch.iterrows():
        try:
            user_message = create_natural_language_prompt(row, previous_visit_info.get(row['PatientID']))
            assistant_message = {
                "role": "assistant",
                "content": row['MedicalNotes'].rstrip('.').strip() + "."
            }
            jsonl_entry = {
                "messages": [user_message, assistant_message]
            }
            jsonl_entries.append(jsonl_entry)
            
            # Update previous_visit_info for this patient
            previous_visit_info[row['PatientID']] = row
        except Exception as e:
            print(f"Error processing row {idx}:")
            print(f"Error details: {str(e)}")
            print("Row data:")
            print(row)
    return jsonl_entries, previous_visit_info

# Process the DataFrame in batches
batch_size = 1000
jsonl_entries = []
previous_visit_info = {}

for start in range(0, len(df), batch_size):
    end = start + batch_size
    batch = df.iloc[start:end]
    batch_entries, previous_visit_info = process_batch(batch, previous_visit_info)
    jsonl_entries.extend(batch_entries)
    print(f"Processed {end} out of {len(df)} entries")

print(f"\nTotal entries processed: {len(jsonl_entries)}")

# Write the JSONL entries to a file
with open(output_jsonl_path, 'w', encoding='utf-8') as f:
    for entry in jsonl_entries:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"JSONL dataset created at: {output_jsonl_path}")
print(f"Final count of entries processed: {len(jsonl_entries)}")