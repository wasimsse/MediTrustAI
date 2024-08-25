import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import calendar
import tkinter as tk
from tkinter import filedialog

# Output directory
OUTPUT_DIR = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\useable'

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def correct_impossible_date(date_string):
    if pd.isna(date_string) or not isinstance(date_string, str):
        return None
    try:
        if '-' in date_string:  # Format: YYYY-MM-DD
            year, month, day = map(int, date_string.split('-'))
        elif '/' in date_string:  # Format: M/D/YYYY
            month, day, year = map(int, date_string.split('/'))
        else:
            return None

        if year > 2024:
            year = int(f"19{year % 100}")  # Correct year to 19xx
        if month > 12:
            month = 12
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)
        return f"{month:02d}/{day:02d}/{year}"
    except ValueError:
        return None

def parse_date(date_string):
    if pd.isna(date_string):
        return None
    corrected_date = correct_impossible_date(date_string)
    if corrected_date:
        try:
            return datetime.strptime(corrected_date, "%m/%d/%Y")
        except ValueError:
            return None
    return None

def calculate_age(dob, visit_date):
    if pd.isna(dob) or pd.isna(visit_date):
        return None
    
    # Convert pandas Timestamp to Python datetime if necessary
    if isinstance(dob, pd.Timestamp):
        dob = dob.to_pydatetime()
    if isinstance(visit_date, pd.Timestamp):
        visit_date = visit_date.to_pydatetime()
    
    # Ensure dob is not later than visit_date
    if dob > visit_date:
        return 0
    
    years = visit_date.year - dob.year
    
    # Check if birthday has occurred this year
    if (visit_date.month, visit_date.day) < (dob.month, dob.day):
        years -= 1
    
    # Calculate days for decimal part
    if dob.month == 2 and dob.day == 29 and not is_leap_year(visit_date.year):
        last_birthday = datetime(visit_date.year, 3, 1)
    else:
        try:
            last_birthday = dob.replace(year=visit_date.year)
        except ValueError:
            # Handle February 29 in non-leap years
            last_birthday = datetime(visit_date.year, 3, 1)
    
    if last_birthday > visit_date:
        try:
            last_birthday = last_birthday.replace(year=last_birthday.year - 1)
        except ValueError:
            # Handle February 29 again
            last_birthday = datetime(last_birthday.year - 1, 3, 1)
    
    days_since_last_birthday = (visit_date - last_birthday).days
    
    # Count leap days between last birthday and visit date
    leap_days = sum(1 for year in range(last_birthday.year, visit_date.year + 1) 
                    if is_leap_year(year) and datetime(year, 2, 29) <= visit_date 
                    and datetime(year, 2, 29) > last_birthday)
    
    # Adjust for leap days
    days_since_last_birthday -= leap_days
    
    # Calculate decimal part
    days_in_year = 366 if is_leap_year(last_birthday.year) else 365
    decimal_part = days_since_last_birthday / days_in_year
    
    return years + decimal_part

def determine_age_group(age):
    if pd.isna(age):
        return "Unknown"
    if age < 28/365:
        return "Neonates"
    elif age < 1:
        return "Infants"
    elif age < 6:
        return "Toddlers and Preschoolers"
    elif age < 13:
        return "School-Age Children"
    elif age < 19:
        return "Adolescents"
    elif age < 65:
        return "Adults"
    else:
        return "Elderly"

def process_csv():
    # Prompt for input file
    root = tk.Tk()
    root.withdraw()
    input_file = filedialog.askopenfilename(
        initialdir=r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\forhistory\formatted\appended',
        title="Select CSV file",
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
    )
    if not input_file:
        print("No file selected. Exiting.")
        return

    # Read the CSV file
    df = pd.read_csv(input_file, low_memory=False, encoding='utf-8-sig')

    # Correct and parse DateOfBirth and VisitDate
    df['CorrectedDateOfBirth'] = df['DateOfBirth'].apply(correct_impossible_date)
    df['ParsedDateOfBirth'] = df['CorrectedDateOfBirth'].apply(parse_date)
    df['ParsedVisitDate'] = df['VisitDate'].apply(parse_date)

    # Calculate Age and AgeGroup for each visit
    df['Age'] = df.apply(lambda row: calculate_age(row['ParsedDateOfBirth'], row['ParsedVisitDate']), axis=1)
    df['AgeGroup'] = df['Age'].apply(determine_age_group)

    # Update the original DateOfBirth column with the corrected version
    df['DateOfBirth'] = df['CorrectedDateOfBirth'].fillna(df['DateOfBirth'])

    # Reorder columns
    columns = df.columns.tolist()
    dob_index = columns.index('DateOfBirth')
    
    # Remove Age and AgeGroup from their current positions
    if 'Age' in columns:
        columns.remove('Age')
    if 'AgeGroup' in columns:
        columns.remove('AgeGroup')
    
    # Insert Age and AgeGroup after DateOfBirth
    columns.insert(dob_index + 1, 'Age')
    columns.insert(dob_index + 2, 'AgeGroup')
    
    # Remove temporary columns
    columns = [col for col in columns if col not in ['CorrectedDateOfBirth', 'ParsedDateOfBirth', 'ParsedVisitDate']]
    
    # Reorder the DataFrame
    df = df[columns]

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate output filename
    input_filename = os.path.basename(input_file)
    output_filename = os.path.splitext(input_filename)[0] + '_vAM.csv'
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    # Save the processed DataFrame to a new CSV file
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Processed file saved to: {output_file}")

if __name__ == "__main__":
    process_csv()