import os
import pandas as pd
import gradio as gr

# Construct the full path to the data file
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/TestData.xlsx'))
print(f"Looking for data file at: {data_path}")

# Load the data from the Excel file
try:
    df = pd.read_excel(data_path)
    print("Data loaded successfully")
except FileNotFoundError as e:
    print(f"File not found: {data_path}")
    print("Current directory contents:")
    print(os.listdir('.'))
    print("Parent directory contents:")
    print(os.listdir('..'))
    raise e

# Function to get patient information by SSN
def get_patient_info(ssn):
    try:
        patient_info = df[df['PatientID'] == ssn]
        if patient_info.empty:
            return f"No information found for SSN: {ssn}"
        else:
            return patient_info.to_dict(orient='records')[0]
    except Exception as e:
        return f"An error occurred: {e}"

# Doctor interface
def doctor_interface(ssn):
    return get_patient_info(ssn)

# Patient interface
def patient_interface(ssn):
    return get_patient_info(ssn)

# Researcher interface
def researcher_interface():
    return df.describe().to_dict()

# Create Gradio interfaces
doctor_demo = gr.Interface(
    fn=doctor_interface,
    inputs=gr.Textbox(label="Enter patient SSN to retrieve information.", placeholder="Enter SSN"),
    outputs="json",
    title="Doctor Interface",
    description="Interface for doctors to retrieve and update patient information."
)

patient_demo = gr.Interface(
    fn=patient_interface,
    inputs=gr.Textbox(label="Enter your SSN to retrieve your information.", placeholder="Enter SSN"),
    outputs="json",
    title="Patient Interface",
    description="Interface for patients to view their medical history."
)

researcher_demo = gr.Interface(
    fn=researcher_interface,
    inputs=None,
    outputs="json",
    title="Researcher Interface",
    description="Interface for researchers to view aggregated data."
)

# Create a tabbed interface
demo = gr.TabbedInterface(
    [doctor_demo, patient_demo, researcher_demo],
    ["Doctor", "Patient", "Researcher"]
)

if __name__ == "__main__":
    demo.launch()
