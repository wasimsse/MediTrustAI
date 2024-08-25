import gradio as gr
import sys
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Add the directory containing your modules to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data_anonymization/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data_translation/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../text_summarization/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../prompt_engineering/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../critical_analysis/src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../llm_fine_tuning/src')))

from faker_anonymizer import anonymize_text, de_anonymize_text, fake_name, fake_phone_number, fake_email, fake_date_birth
from data_translation import translate_text
from summarizer import summarize_text, verify_summary_accuracy
from prompt_engine import generate_prompt
from analysis import analyze_text
from fine_tune_model import fine_tune_model

# Function to fine-tune LLM
def fine_tune_interface(model_name, dataset_name, output_dir):
    try:
        fine_tune_model(model_name, dataset_name, output_dir)
        return f"Model fine-tuned and saved to {output_dir}"
    except Exception as e:
        return f"Error during fine-tuning: {str(e)}"

# Function to answer in Finnish
def finnish_answer_interface(text):
    try:
        translated_text = translate_text(text)
        # Placeholder for LLM model to generate an answer in Finnish
        answer = "Tämä on esimerkki suomeksi."
        return answer
    except Exception as e:
        return f"Error generating Finnish answer: {str(e)}"

def anonymize_interface(text):
    try:
        anonymized_text, analyzer_results = anonymize_text(text)
        return anonymized_text
    except Exception as e:
        return f"Error during anonymization: {str(e)}"

def de_anonymize_interface(anonymized_text, original_text):
    try:
        entity_mapping = {
            fake_name(None): "Allan Mask",
            fake_phone_number(None): "+358 409876541",
            fake_email(None): "allan.mask@example.com",
            fake_date_birth(None): "2021-12-25"
        }
        de_anonymized_text = de_anonymize_text(anonymized_text, entity_mapping)
        return de_anonymized_text
    except Exception as e:
        return f"Error during de-anonymization: {str(e)}"

def translation_interface(text):
    try:
        return translate_text(text)
    except Exception as e:
        return f"Error during translation: {str(e)}"

def summarization_interface(text, detail_level="high", format_structure="bullet_points", include_medications=True, include_allergies=True, include_lab_results=True):
    try:
        summary = summarize_text(text, detail_level, format_structure, include_medications, include_allergies, include_lab_results)
        verification_results = verify_summary_accuracy(text, summary)
        return summary, verification_results
    except Exception as e:
        return f"Error during summarization: {str(e)}"

def prompt_engine_interface(prompt):
    try:
        return generate_prompt(prompt)
    except Exception as e:
        return f"Error during prompt generation: {str(e)}"

def critical_analysis_interface(text):
    try:
        return analyze_text(text)
    except Exception as e:
        return f"Error during critical analysis: {str(e)}"

def multi_agent_verification(summary, original_text):
    try:
        # Load Sentence Transformer model for semantic similarity
        sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # Encode original text and summary
        original_embedding = sbert_model.encode([original_text])
        summary_embedding = sbert_model.encode([summary])

        # Calculate cosine similarity
        similarity = cosine_similarity(original_embedding, summary_embedding)[0][0]

        # Perform verification
        accuracy = similarity > 0.7
        relevance = 'medication' in summary.lower() or 'allergy' in summary.lower() or 'lab results' in summary.lower()
        consistency = not any(summary.count(x) > 1 for x in summary.split())

        verification_result = {
            "accuracy": accuracy,
            "relevance": relevance,
            "consistency": consistency,
            "is_valid": accuracy and relevance and consistency
        }

        return verification_result
    except Exception as e:
        return {
            "accuracy": False,
            "relevance": False,
            "consistency": False,
            "is_valid": False,
            "error": str(e)
        }

def anonymize_file_interface(file):
    try:
        df = pd.read_csv(file.name)
        anonymized_data = df.applymap(lambda x: anonymize_text(x)[0] if isinstance(x, str) else x)
        anonymized_file = "anonymized_data.csv"
        anonymized_data.to_csv(anonymized_file, index=False)
        return anonymized_file
    except Exception as e:
        return f"Error during file anonymization: {str(e)}"

def de_anonymize_file_interface(anonymized_file, entity_mapping_file):
    try:
        df_anonymized = pd.read_csv(anonymized_file.name)
        entity_mapping = pd.read_json(entity_mapping_file.name).to_dict(orient='records')[0]
        de_anonymized_data = df_anonymized.applymap(lambda x: de_anonymize_text(x, entity_mapping) if isinstance(x, str) else x)
        de_anonymized_file = "de_anonymized_data.csv"
        de_anonymized_data.to_csv(de_anonymized_file, index=False)
        return de_anonymized_file
    except Exception as e:
        return f"Error during file de-anonymization: {str(e)}"

anonymize_demo = gr.Interface(
    fn=anonymize_interface,
    inputs=gr.Textbox(lines=10, placeholder="Enter text to anonymize...", label="Text to Anonymize"),
    outputs="text",
    title="Data Anonymization",
    description="Anonymize sensitive information in the text.",
    css="gui/static/style.css"
)

de_anonymize_demo = gr.Interface(
    fn=de_anonymize_interface,
    inputs=[gr.Textbox(lines=10, placeholder="Enter anonymized text...", label="Anonymized Text"), gr.Textbox(lines=10, placeholder="Enter original text for mapping...", label="Original Text for Mapping")],
    outputs="text",
    title="Data De-anonymization",
    description="De-anonymize the text using the original mapping.",
    css="gui/static/style.css"
)

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

translation_demo = gr.Interface(
    fn=translation_interface,
    inputs=gr.Textbox(lines=10, placeholder="Enter text to translate...", label="Text to Translate"),
    outputs="text",
    title="Data Translation",
    description="Translate text from one language to another.",
    css="gui/static/style.css"
)

summarization_demo = gr.Interface(
    fn=summarization_interface,
    inputs=[
        gr.Textbox(lines=10, placeholder="Enter text to summarize...", label="Text to Summarize"),
        gr.Dropdown(choices=['high', 'balanced', 'low'], label="Detail Level"),
        gr.Dropdown(choices=['narrative', 'bullet_points', 'soap_note'], label="Format Structure"),
        gr.Checkbox(label="Include Medications", value=True),
        gr.Checkbox(label="Include Allergies", value=True),
        gr.Checkbox(label="Include Lab Results", value=True)
    ],
    outputs=["text", "json"],
    title="Text Summarization",
    description="Summarize medical texts based on doctor preferences.",
    css="gui/static/style.css"
)

prompt_engine_demo = gr.Interface(
    fn=prompt_engine_interface,
    inputs=gr.Textbox(lines=10, placeholder="Enter prompt text...", label="Prompt Text"),
    outputs="text",
    title="Prompt Engineering",
    description="Generate prompts for AI models.",
    css="gui/static/style.css"
)

critical_analysis_demo = gr.Interface(
    fn=critical_analysis_interface,
    inputs=gr.Textbox(lines=10, placeholder="Enter text for analysis...", label="Text for Analysis"),
    outputs="text",
    title="Critical Analysis",
    description="Analyze critical medical texts.",
    css="gui/static/style.css"
)

fine_tune_demo = gr.Interface(
    fn=fine_tune_interface,
    inputs=[
        gr.Textbox(lines=1, placeholder="Enter model name...", label="Model Name"),
        gr.Textbox(lines=1, placeholder="Enter dataset name...", label="Dataset Name"),
        gr.Textbox(lines=1, placeholder="Enter output directory...", label="Output Directory")
    ],
    outputs="text",
    title="LLM Fine-Tuning",
    description="Fine-tune language models for specific tasks.",
    css="gui/static/style.css"
)

finnish_answer_demo = gr.Interface(
    fn=finnish_answer_interface,
    inputs=gr.Textbox(lines=10, placeholder="Enter text to get answer in Finnish...", label="Text"),
    outputs="text",
    title="Answer in Finnish",
    description="Get answers in Finnish language.",
    css="gui/static/style.css"
)

multi_agent_demo = gr.Interface(
    fn=multi_agent_verification,
    inputs=[gr.Textbox(lines=10, placeholder="Enter summarized text...", label="Summarized Text"), gr.Textbox(lines=10, placeholder="Enter original text...", label="Original Text")],
    outputs="json",
    title="Multi-Agent Verification",
    description="Verify the summarized text against the original text.",
    css="gui/static/style.css"
)

demo = gr.TabbedInterface(
    [
        anonymize_demo,
        de_anonymize_demo,
        anonymize_file_demo,
        de_anonymize_file_demo,
        translation_demo,
        summarization_demo,
        prompt_engine_demo,
        critical_analysis_demo,
        fine_tune_demo,
        finnish_answer_demo,
        multi_agent_demo
    ],
    ["Anonymize Text", "De-anonymize Text", "Anonymize File", "De-anonymize File", "Translate", "Summarize", "Prompt Engineering", "Critical Analysis", "Fine-Tune LLM", "Answer in Finnish", "Multi-Agent Verification"],
    css="gui/static/style.css"
)

if __name__ == "__main__":
    demo.launch()
