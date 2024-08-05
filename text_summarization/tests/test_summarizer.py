from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load the model and tokenizer
model_name = 't5-small'  # Update this with the correct model name if different
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
except Exception as e:
    print(f"Error loading model {model_name}: {str(e)}")
    tokenizer, model = None, None

# Load Sentence Transformer model for semantic similarity
try:
    sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading Sentence Transformer model: {str(e)}")
    sbert_model = None

def summarize_text(text, detail_level="high", format_structure="bullet_points", include_medications=True, include_allergies=True, include_lab_results=True):
    if tokenizer is None or model is None or sbert_model is None:
        return "Error: Models are not loaded properly."

    try:
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Remove redundant sentences
        sentences = summary.split('. ')
        sentence_embeddings = sbert_model.encode(sentences)
        redundancy_threshold = 0.8  # Threshold for considering sentences redundant

        non_redundant_sentences = []
        for i, sentence in enumerate(sentences):
            is_redundant = False
            for j in range(i):
                if cosine_similarity([sentence_embeddings[i]], [sentence_embeddings[j]]) > redundancy_threshold:
                    is_redundant = True
                    break
            if not is_redundant:
                non_redundant_sentences.append(sentence)

        clean_summary = '. '.join(non_redundant_sentences)

        # Ensure important details are included
        if include_medications and "medications" not in text.lower() and "medication" not in text.lower():
            clean_summary += "\n- Include medications details."
        if include_allergies and "allergies" not in text.lower() and "allergy" not in text.lower():
            clean_summary += "\n- Include allergy details."
        if include_lab_results and "lab results" not in text.lower() and "lab result" not in text.lower():
            clean_summary += "\n- Include lab results details."

        # Format the summary
        if format_structure == "bullet_points":
            clean_summary = '\n- '.join([''] + clean_summary.split('. '))

        return clean_summary
    except Exception as e:
        return f"Error during summarization: {str(e)}"

def verify_summary_accuracy(original_text, summary_text):
    try:
        # Compute semantic similarity
        original_embedding = sbert_model.encode([original_text])
        summary_embedding = sbert_model.encode([summary_text])
        similarity = cosine_similarity(original_embedding, summary_embedding)[0][0]

        # Define relevance and consistency thresholds
        relevance = similarity > 0.5
        consistency = similarity > 0.7

        # Validity check based on predefined criteria
        is_valid = relevance and consistency

        return {
            "accuracy": similarity > 0.7,
            "relevance": relevance,
            "consistency": consistency,
            "is_valid": is_valid
        }
    except Exception as e:
        return {
            "accuracy": False,
            "relevance": False,
            "consistency": False,
            "is_valid": False,
            "error": str(e)
        }
