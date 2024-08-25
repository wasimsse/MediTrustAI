import pandas as pd
import hashlib
import json
import re
import gradio as gr
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig

# Initialize Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Dictionary to hold mappings for de-anonymization
token_map = {}

# Function to generate a token for a given value
def generate_token(value):
    token = hashlib.sha256(value.encode()).hexdigest()
    token_map[token] = value
    return token

# Function to anonymize a value based on its field type
def anonymize_value(value, field_type):
    if field_type == 'name':
        return "[PERSON]"
    elif field_type == 'date':
        value = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', 'YYYY-MM-DD', value)
        value = re.sub(r'\b\d{2}-\d{2}-\d{4}\b', 'MM-DD-YYYY', value)
        value = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', 'DD-MM-YYYY', value)
        value = re.sub(r'\b\d{2}/\d{2}/\d{2}\b', 'MM/DD/YY', value)
        return value
    elif field_type == 'address':
        return "[LOCATION]"
    elif field_type == 'id':
        return generate_token(value)
    elif field_type == 'email':
        return generate_token(value)
    elif field_type == 'phone':
        return generate_token(value)
    elif field_type == 'financial':
        return "[FINANCIAL]"
    elif field_type == 'ssn':
        return "[SSN]"
    else:
        return value

# Function to detect the field type based on the column name
def detect_field_type(column_name):
    column_name = column_name.lower()
    if 'name' in column_name:
        return 'name'
    elif 'date' in column_name or 'birth' in column_name:
        return 'date'
    elif 'address' in column_name:
        return 'address'
    elif 'id' in column_name or 'ssn' in column_name:
        return 'id'
    elif 'email' in column_name:
        return 'email'
    elif 'phone' in column_name:
        return 'phone'
    elif 'financial' in column_name or 'account' in column_name:
        return 'financial'
    else:
        return 'other'

# Function to anonymize data in a dataframe
def anonymize_data(df):
    for column in df.columns:
        field_type = detect_field_type(column)
        if field_type in ['name', 'date', 'address', 'id', 'email', 'phone', 'financial', 'ssn']:
            df[column] = df[column].apply(lambda x: anonymize_value(str(x), field_type) if pd.notnull(x) else x)
    return df

# Function to anonymize text in medical notes using Presidio
def anonymize_notes(text):
    results = analyzer.analyze(text=text, language='en')
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results, operators={
        "PERSON": OperatorConfig("replace", {"new_value": "[PERSON]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATE]"}),
        "EMAIL": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "US_BANK_NUMBER": OperatorConfig("replace", {"new_value": "[BANK]"}),
        "US_SSN": OperatorConfig("replace", {"new_value": "[SSN]"})
    })
    return anonymized_result.text

# Function to save the token map to a file
def save_token_map(file_path):
    with open(file_path, 'w') as file:
        json.dump(token_map, file)

# Function to load the token map from a file
def load_token_map(file_path):
    global token_map
    with open(file_path, 'r') as file:
        token_map = json.load(file)

# Function to anonymize data from an uploaded Excel file
def anonymize_file(file):
    try:
        df = pd.read_excel(file.name)
        anonymized_data = anonymize_data(df.copy())
        if 'MedicalNotes' in anonymized_data.columns:
            anonymized_data['MedicalNotes'] = anonymized_data['MedicalNotes'].apply(anonymize_notes)
        anonymized_file = "anonymized_data.xlsx"
        anonymized_data.to_excel(anonymized_file, index=False)
        save_token_map('token_map.json')
        return anonymized_file
    except Exception as e:
        return f"Error during anonymization: {e}"

# Function to de-anonymize data from an uploaded Excel file
def de_anonymize_file(file):
    try:
        load_token_map('token_map.json')
        df_anonymized = pd.read_excel(file.name)
        de_anonymized_data = de_anonymize_data(df_anonymized.copy())
        de_anonymized_file = "de_anonymized_data.xlsx"
        de_anonymized_data.to_excel(de_anonymized_file, index=False)
        return de_anonymized_file
    except Exception as e:
        return f"Error during de-anonymization: {e}"

def de_anonymize_data(df):
    for column in df.columns:
        field_type = detect_field_type(column)
        if field_type in ['id', 'email', 'phone', 'financial', 'ssn']:
            df[column] = df[column].apply(lambda x: de_anonymize_value(str(x)) if pd.notnull(x) else x)
        else:
            df[column] = df[column].apply(lambda x: token_map.get(x, x) if x in token_map.values() else x)
    return df

def de_anonymize_value(value):
    return token_map.get(value, value)

# Function to verify anonymization
def verify_anonymization(df, original_df):
    issues = []
    for column in df.columns:
        field_type = detect_field_type(column)
        if field_type in ['id', 'email', 'phone', 'financial', 'ssn']:
            for original_value, anonymized_value in zip(original_df[column], df[column]):
                if original_value and anonymized_value and anonymized_value in token_map:
                    if token_map[anonymized_value] != original_value:
                        issues.append((original_value, anonymized_value))
        else:
            for original_value, anonymized_value in zip(original_df[column], df[column]):
                if original_value and anonymized_value and original_value == anonymized_value:
                    issues.append((original_value, anonymized_value))
    return issues

# Function to cross-check anonymization
def cross_check_anonymization(df, original_df):
    issues = []
    for column in df.columns:
        for original_value, anonymized_value in zip(original_df[column], df[column]):
            if original_value and anonymized_value and anonymized_value == original_value:
                issues.append((original_value, anonymized_value))
    return issues

# Function to verify anonymization via the Gradio interface
def verify_anonymization_interface(file):
    try:
        original_data = pd.read_excel(file.name)
        anonymized_data = anonymize_data(original_data.copy())
        
        # Verify anonymization with the secondary agent
        issues = verify_anonymization(anonymized_data, original_data)
        if issues:
            return f"Anonymization Issues Found: {issues}"
        
        # Cross-check anonymization with the cross-checking agent
        cross_check_issues = cross_check_anonymization(anonymized_data, original_data)
        if cross_check_issues:
            return f"Cross-Check Issues Found: {cross_check_issues}"
        
        return "Anonymization Verified Successfully"
    except Exception as e:
        return f"Error during verification: {e}"

# Define the Gradio interfaces
anonymize_interface = gr.Interface(
    fn=anonymize_file,
    inputs=gr.File(label="Upload Excel file to anonymize"),
    outputs="file",
    title="File Anonymization",
    description="Anonymize sensitive information in the uploaded Excel file."
)

de_anonymize_interface = gr.Interface(
    fn=de_anonymize_file,
    inputs=gr.File(label="Upload anonymized Excel file"),
    outputs="file",
    title="File De-anonymization",
    description="De-anonymize the uploaded Excel file using the saved token map."
)

verify_anonymization_interface = gr.Interface(
    fn=verify_anonymization_interface,
    inputs=gr.File(label="Upload original Excel file"),
    outputs="text",
    title="Verify Anonymization",
    description="Verify the anonymization of the uploaded Excel file."
)

# Combine the interfaces into a single Gradio application
demo = gr.TabbedInterface(
    [anonymize_interface, de_anonymize_interface, verify_anonymization_interface],
    ["Anonymize File", "De-anonymize File", "Verify Anonymization"],
    title="Data Anonymization and De-anonymization Tool"
)

if __name__ == "__main__":
    demo.launch()
