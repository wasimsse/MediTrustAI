import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from tqdm import tqdm
tqdm.pandas()

# File paths
input_file = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable\appended_20240806_093139.csv'
output_file = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable\cleaned_appended_20240806_093139.csv'

def calculate_age_and_group(dob, visit_date):
    if pd.isnull(dob) or pd.isnull(visit_date):
        return np.nan, "Unknown"
    
    age = visit_date.year - dob.year - ((visit_date.month, visit_date.day) < (dob.month, dob.day))
    
    if age < 0 or age > 120:  # Assuming maximum age of 120 years
        return np.nan, "Unknown"
    elif age < 28/365:
        return age, "Neonates"
    elif age < 1:
        return age, "Infants"
    elif age < 6:
        return age, "Toddlers and Preschoolers"
    elif age < 13:
        return age, "School-Age Children"
    elif age < 19:
        return age, "Adolescents"
    elif age < 65:
        return age, "Adults"
    else:
        return age, "Elderly"

def extract_blood_pressure(bp_string):
    if pd.isna(bp_string):
        return np.nan, np.nan
    match = re.search(r'(\d{2,3})/(\d{2,3})', str(bp_string))
    if match:
        return float(match.group(1)), float(match.group(2))
    return np.nan, np.nan

def extract_spo2(spo2_string):
    if pd.isna(spo2_string):
        return np.nan
    match = re.search(r'(\d{1,3})%?', str(spo2_string))
    if match:
        return float(match.group(1))
    return np.nan

def impute_dates(row):
    if pd.isna(row['DateOfBirth']) and pd.notna(row['VisitDate']) and pd.notna(row['Age']):
        return row['VisitDate'] - pd.Timedelta(days=int(row['Age']*365.25))
    elif pd.isna(row['VisitDate']) and pd.notna(row['DateOfBirth']) and pd.notna(row['Age']):
        return row['DateOfBirth'] + pd.Timedelta(days=int(row['Age']*365.25))
    return row['DateOfBirth'] if pd.notna(row['DateOfBirth']) else row['VisitDate']

def clean_data(df):
    print("Dropping duplicate columns...")
    if 'Age.1' in df.columns and 'AgeGroup.1' in df.columns:
        df = df.drop(['Age.1', 'AgeGroup.1'], axis=1)
    
    print("Replacing 'None'-like values...")
    none_like_values = ['None', 'N/A', 'n/a', 'NA', 'null', 'NULL']
    df = df.replace(none_like_values, np.nan)
    
    print("Converting dates to datetime...")
    df['DateOfBirth'] = pd.to_datetime(df['DateOfBirth'], errors='coerce')
    df['VisitDate'] = pd.to_datetime(df['VisitDate'], errors='coerce')
    
    print("Imputing missing dates...")
    tqdm.pandas(desc="Imputing dates")
    df['ImputedDate'] = df.progress_apply(impute_dates, axis=1)
    df['DateOfBirth'] = df.apply(lambda row: row['ImputedDate'] if pd.isna(row['DateOfBirth']) else row['DateOfBirth'], axis=1)
    df['VisitDate'] = df.apply(lambda row: row['ImputedDate'] if pd.isna(row['VisitDate']) else row['VisitDate'], axis=1)
    df = df.drop('ImputedDate', axis=1)
    
    print("Recalculating Age and AgeGroup...")
    tqdm.pandas(desc="Calculating age")
    df[['Age', 'AgeGroup']] = df.progress_apply(lambda row: pd.Series(calculate_age_and_group(row['DateOfBirth'], row['VisitDate'])), axis=1)
    
    print("Handling Blood Pressure...")
    tqdm.pandas(desc="Processing Blood Pressure")
    df[['Systolic', 'Diastolic']] = df['BloodPressure'].progress_apply(extract_blood_pressure).tolist()
    df['BloodPressure'] = df.apply(lambda row: f"{int(row['Systolic'])}/{int(row['Diastolic'])}" if pd.notna(row['Systolic']) and pd.notna(row['Diastolic']) else np.nan, axis=1)
    df = df.drop(['Systolic', 'Diastolic'], axis=1)
    
    print("Handling SpO2...")
    tqdm.pandas(desc="Processing SpO2")
    df['SpO2'] = df['SpO2'].progress_apply(extract_spo2)
    df['SpO2'] = df['SpO2'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else np.nan)
    
    print("Converting vital signs to numeric...")
    numeric_columns = ['Pulse', 'Temperature', 'Weight', 'Height']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print("Imputing missing values for vital signs...")
    vital_signs = ['BloodPressure', 'Pulse', 'SpO2', 'Temperature', 'Weight', 'Height']
    for col in tqdm(vital_signs, desc="Imputing vital signs"):
        df[col] = df.groupby('PatientID')[col].fillna(method='ffill').fillna(method='bfill')
    
    print("Filling categorical columns...")
    categorical_fills = {
        'Gender': 'Unknown',
        'InitialCondition': 'Not specified',
        'LongTermConditions': 'None reported',
        'SecondaryConditions': 'None reported',
        'Allergies': 'None reported',
        'MedicationHistory': 'None reported',
        'VisitType': 'Not specified',
        'Symptoms': 'Not reported',
        'Diagnosis': 'Not specified',
        'MedicationPrescribed': 'None prescribed',
        'LabResults': 'Not performed',
        'Procedures': 'None performed',
        'MedicalNotes': 'No notes'
    }
    
    for col, fill_value in tqdm(categorical_fills.items(), desc="Filling categorical data"):
        df[col] = df[col].fillna(fill_value)
    
    return df

def main():
    print("Reading CSV file...")
    df = pd.read_csv(input_file, encoding='utf-8-sig', low_memory=False)
    print(f"Read {len(df)} rows.")
    
    print("Cleaning data...")
    cleaned_df = clean_data(df)
    
    print("Saving cleaned data...")
    cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Cleaned data saved to {output_file}")
    print("\nCleaning summary:")
    print(f"Original shape: {df.shape}")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print("\nRemaining null values:")
    print(cleaned_df.isnull().sum())

if __name__ == "__main__":
    main()