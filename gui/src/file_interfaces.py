import gradio as gr
import pandas as pd
from faker_anonymizer import anonymize_text, de_anonymize_text

def anonymize_file_interface(file):
    try:
        df = pd.read_csv(file.name)
        df_anonymized = df.applymap(lambda x: anonymize_text(str(x))[0] if isinstance(x, str) else x)
        anonymized_file = "anonymized_output.csv"
        df_anonymized.to_csv(anonymized_file, index=False)
        return anonymized_file
    except Exception as e:
        return f"Error during file anonymization: {str(e)}"

def de_anonymize_file_interface(anonymized_file, entity_mapping_file):
    try:
        df_anonymized = pd.read_csv(anonymized_file.name)
        entity_mapping = pd.read_json(entity_mapping_file.name).to_dict(orient='records')[0]
        df_deanonymized = df_anonymized.applymap(lambda x: de_anonymize_text(x, entity_mapping) if isinstance(x, str) else x)
        de_anonymized_file = "de_anonymized_output.csv"
        df_deanonymized.to_csv(de_anonymized_file, index=False)
        return de_anonymized_file
    except Exception as e:
        return f"Error during file de-anonymization: {str(e)}"

anonymize_file_demo = gr.Interface(
    fn=anonymize_file_interface,
    inputs=gr.File(label="Upload CSV file to anonymize"),
    outputs="file",
    title="File Anonymization",
    description="Anonymize sensitive information in the uploaded CSV file.",
    css="gui/static/style.css"
)

de_anonymize_file_demo = gr.Interface(
    fn=de_anonymize_file_interface,
    inputs=[gr.File(label="Upload anonymized CSV file"), gr.File(label="Upload entity mapping JSON file")],
    outputs="file",
    title="File De-anonymization",
    description="De-anonymize the uploaded CSV file using the entity mapping JSON file.",
    css="gui/static/style.css"
)
