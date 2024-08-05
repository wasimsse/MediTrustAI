import gradio as gr
from gradio_interfaces import (
    anonymize_demo, de_anonymize_demo, translation_demo,
    summarization_demo, prompt_engine_demo, critical_analysis_demo
)

def main():
    with gr.Blocks() as demo:
        gr.Markdown("# AI-Based Data Processing Application")

        with gr.Tab("Data Anonymization"):
            anonymize_demo.render()

        with gr.Tab("Data De-anonymization"):
            de_anonymize_demo.render()

        with gr.Tab("Data Translation"):
            translation_demo.render()

        with gr.Tab("Text Summarization"):
            summarization_demo.render()

        with gr.Tab("Prompt Engineering"):
            prompt_engine_demo.render()

        with gr.Tab("Critical Analysis"):
            critical_analysis_demo.render()

    demo.launch(share=True)

if __name__ == "__main__":
    main()
