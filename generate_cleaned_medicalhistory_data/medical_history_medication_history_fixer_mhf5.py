import pandas as pd
import os
from datetime import datetime
from tqdm import tqdm
import calendar
import re
import tkinter as tk
from tkinter import filedialog

# Output directory
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable'

# Set to None to process all patients, or a number for partial processing
MAX_PATIENTS = None

def parse_date(date_string):
    if pd.isna(date_string) or not isinstance(date_string, str):
        return None
    
    date_string = date_string.strip()
    
    months = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
        'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    for month_name, month_num in months.items():
        if month_name in date_string:
            date_string = date_string.replace(month_name, month_num)
    
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y %m %d', '%m-%d-%Y', '%d-%m-%Y']
    for date_format in date_formats:
        try:
            date = datetime.strptime(date_string, date_format)
            return date.strftime('%m/%d/%Y')
        except ValueError:
            continue
    
    match = re.search(r'(\d{4}).*?(\d{1,2}).*?(\d{1,2})', date_string)
    if match:
        year, month, day = map(int, match.groups())
        if month > 12:
            month = 12
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)
        return f"{month:02d}/{day:02d}/{year}"
    
    print(f"Unable to parse date: {date_string}")
    return None

def process_medications(prescription):
    if pd.isna(prescription):
        return []
    return [med.strip() for med in prescription.split(',') if med.strip()]

def process_csv():
    # Prompt user for input file
    root = tk.Tk()
    root.withdraw()
    input_file = filedialog.askopenfilename(
        initialdir=r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable',
        title="Select CSV file to process",
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
    )
    if not input_file:
        print("No file selected. Exiting.")
        return

    # Generate output filename
    input_filename = os.path.basename(input_file)
    output_filename = f"medication_history_fixed_{input_filename}"
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    print(f"Reading CSV file: {input_file}")
    df = pd.read_csv(input_file, low_memory=False, encoding='utf-8-sig')
    original_shape = df.shape
    print(f"Original DataFrame shape: {original_shape}")

    print("Processing dates...")
    print("Unique values in VisitDate column:", df['VisitDate'].unique())
    
    df['VisitDate'] = df['VisitDate'].apply(parse_date)
    df['VisitDate'] = pd.to_datetime(df['VisitDate'], format='%m/%d/%Y', errors='coerce')
    
    print("Number of null VisitDate values after parsing:", df['VisitDate'].isnull().sum())
    
    print("Processing medication history...")
    if MAX_PATIENTS:
        unique_patients = df['PatientID'].unique()[:MAX_PATIENTS]
        df = df[df['PatientID'].isin(unique_patients)].copy()
    
    changes_made = 0
    current_patient = None
    cumulative_history = ""

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        if current_patient != row['PatientID']:
            current_patient = row['PatientID']
            cumulative_history = row['MedicationHistory'] if pd.notna(row['MedicationHistory']) else ""
        
        if pd.notna(row['VisitDate']):
            new_prescriptions = process_medications(row['MedicationPrescribed'])
            for prescription in new_prescriptions:
                if cumulative_history:
                    cumulative_history += ", "
                cumulative_history += f"{row['VisitDate'].strftime('%m/%d/%Y')} - {prescription}"
        
        if i == df.index[-1] or df.iloc[i+1]['PatientID'] != current_patient:
            # Last visit for this patient
            if pd.notna(row['VisitDate']):
                new_history = f"History until {row['VisitDate'].strftime('%m/%d/%Y')} - {cumulative_history}"
            else:
                new_history = f"History until [Date Unknown] - {cumulative_history}"
        else:
            new_history = cumulative_history
        
        if new_history != row['MedicationHistory']:
            df.at[i, 'MedicationHistory'] = new_history
            changes_made += 1
    
    print(f"Total changes made: {changes_made}")
    print(f"Updated DataFrame shape: {df.shape}")
    
    print("Saving updated CSV...")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Updated file saved to: {output_file}")
    
    # Verify changes
    print("Verifying changes...")
    df_check = pd.read_csv(output_file, low_memory=False, encoding='utf-8-sig')
    if df_check.equals(df):
        print("Verification successful: Changes were saved correctly.")
    else:
        print("Verification failed: Saved file does not match expected changes.")
    
    print(f"Original file size: {os.path.getsize(input_file)} bytes")
    print(f"New file size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    process_csv()