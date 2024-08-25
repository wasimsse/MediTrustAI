# MediTrustAI

## Overview
MediTrustAI is an advanced healthcare professional assistant that leverages Large Language Models (LLMs) to improve healthcare services in Europe. This project focuses on summarizing extensive healthcare records for efficient consultations, evaluating prescriptions with patient-specific data to ensure safety, and enhancing the trustworthiness of clinical AI applications.

## Features
- **Data Generation**: Generate synthetic medical data, including scenarios involving chronic diseases.
- **Data Anonymization**: Anonymizes synthetic data to ensure compliance with GDPR guidelines.
- **Text Summarization**: Summarizes patient healthcare records quickly, focusing on details relevant to doctors' preferences.
- **Prompt Engineering**: Refines and improves AI-generated prompts to minimize errors and enhance relevance.
- **Conversation Component**: Records and processes conversations between healthcare providers and patients, extracting diagnostic information.
- **GUI**: Provides an easy-to-use interface for healthcare professionals to interact with the MediTrustAI system.
- **Translation Service**: Translates medical text from English to Finnish using the MarianMT model.
- **Health Chatbot Interface**: A Gradio-based chatbot interface that allows healthcare professionals and patients to interact with AI for health-related queries.
- **Databricks Vector Search and RAG Langchain**: Implements a Retrieval-Augmented Generation (RAG) model using Databricks' vector search capabilities to answer health-related queries by retrieving relevant context.
- **Fine-Tuning Large Language Models (LLMs)**: A script for fine-tuning pre-trained language models on specific datasets to adapt them to particular tasks or domains.
- **Multi-Agent Verification**: A system for verifying the accuracy and consistency of AI-generated text summaries using multiple agents.

## Installation
To set up MediTrustAI on your local machine, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MediTrustAI.git
   cd MediTrustAI

2. pip install -r requirements.txt

3. python gui/src/MediTrustAI_GUI.py


## Usage
After installation, MediTrustAI provides different interfaces and functionalities that can be accessed via the GUI. Each interface corresponds to a specific user role or task:

1. Doctor Interface: Retrieve and manage patient information.
2. Patient Interface: View personal medical history.
3. Researcher Interface: Analyze aggregated patient data.

## Contributing
Contributions to MediTrustAI are welcome! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request. Make sure to follow the contribution guidelines.