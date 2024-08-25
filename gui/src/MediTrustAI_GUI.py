import gradio as gr
from hospital_management import (
    authenticate,
    view_patient_history,
    add_modify_patient_record,
    view_personal_history,
    view_anonymized_data
)

# Doctor Interface
def doctor_interface():
    with gr.Blocks() as dr_interface:
        with gr.Row():
            ssn = gr.Textbox(label="Patient SSN")
            history = gr.Textbox(label="Patient History", interactive=True)
            medications = gr.Textbox(label="Medications", interactive=True)
            notes = gr.Textbox(label="Doctor's Notes", interactive=True)
            allergies = gr.Textbox(label="Allergies", interactive=True)
        view_button = gr.Button("View History")
        update_button = gr.Button("Update History")
        
        view_button.click(view_patient_history, inputs=ssn, outputs=history)
        update_button.click(add_modify_patient_record, inputs=[ssn, "name", "age", "gender", history, medications, notes, allergies], outputs="text")
    return dr_interface

# Patient Interface
def patient_interface(user_data):
    with gr.Blocks() as pt_interface:
        ssn = user_data['ssn']
        history = gr.Textbox(value=user_data['history'], label="Your Medical History", interactive=False)
        medications = gr.Textbox(value=user_data['medications'], label="Your Medications", interactive=False)
        notes = gr.Textbox(value=user_data['notes'], label="Doctor's Notes", interactive=False)
        allergies = gr.Textbox(value=user_data['allergies'], label="Your Allergies", interactive=False)
    return pt_interface

# Researcher Interface
def researcher_interface():
    with gr.Blocks() as res_interface:
        data_button = gr.Button("View Anonymized Data")
        data_table = gr.DataFrame(headers=["SSN", "Name", "Age", "Gender", "History", "Medications", "Notes", "Allergies"], interactive=False)
        
        data_button.click(view_anonymized_data, outputs=data_table)
    return res_interface

# Main Interface
def main_interface():
    with gr.Blocks() as main_interface:
        username = gr.Textbox(label="Username")
        ssn = gr.Textbox(label="SSN")
        login_button = gr.Button("Login")
        role_output = gr.Textbox(label="Role", interactive=False)
        
        login_button.click(authenticate, inputs=[username, ssn], outputs=[role_output, "user_data"])
        
        role_output.change(doctor_interface, inputs=role_output, outputs="auto", show_if=lambda role: role == "Doctor")
        role_output.change(patient_interface, inputs=["user_data"], outputs="auto", show_if=lambda role: role == "Patient")
        role_output.change(researcher_interface, inputs=role_output, outputs="auto", show_if=lambda role: role == "Researcher")
        
    return main_interface

# Launch the interface
if __name__ == "__main__":
    main_interface().launch()
