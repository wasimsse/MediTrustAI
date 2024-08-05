from transformers import MarianMTModel, MarianTokenizer
import torch

# Initialize the model and tokenizer for translation
model_name = 'Helsinki-NLP/opus-mt-en-fi'  # English to Finnish model
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate_text(text):
    """
    Translate text from English to Finnish.
    
    Args:
    text (str): The text to be translated.
    
    Returns:
    str: The translated text in Finnish.
    """
    try:
        # Tokenize the input text
        inputs = tokenizer.encode(text, return_tensors='pt', truncation=True)
        
        # Generate translation using the model
        translated_tokens = model.generate(inputs, max_length=512)
        
        # Decode the translated tokens to a string
        translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        
        return translated_text
    except Exception as e:
        return f"Error in translation: {e}"

def translate_batch_texts(texts):
    """
    Translate a batch of texts from English to Finnish.
    
    Args:
    texts (list of str): The texts to be translated.
    
    Returns:
    list of str: The translated texts in Finnish.
    """
    try:
        # Tokenize the input texts
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        
        # Generate translations using the model
        translated_tokens = model.generate(**inputs, max_length=512)
        
        # Decode the translated tokens to strings
        translated_texts = [tokenizer.decode(t, skip_special_tokens=True) for t in translated_tokens]
        
        return translated_texts
    except Exception as e:
        return [f"Error in translation: {e}" for _ in texts]

# Example usage
if __name__ == "__main__":
    text = "Hello, how are you?"
    translated_text = translate_text(text)
    print(f"Translated text: {translated_text}")
    
    texts = ["Hello, how are you?", "I am fine, thank you."]
    translated_texts = translate_batch_texts(texts)
    print(f"Translated texts: {translated_texts}")
