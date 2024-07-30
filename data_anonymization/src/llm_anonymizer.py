# conda activate py312_data_anonymizing  

import torch
import outlines.models.transformers
import outlines.models
import outlines
from outlines.models.transformers import Transformers
from pydantic import BaseModel, Field 
from typing import Dict

######## LLM based approach ################
to_kwargs = lambda **kwargs: kwargs
model_id = "microsoft/Phi-3-mini-4k-instruct"
model = outlines.models.transformers(model_id, model_kwargs=to_kwargs(trust_remote_code=True, torch_dtype="auto",
                                    device_map="cuda", attn_implementation='eager',
                                    #attn_implmentation="flash_attention_2",
                                    cache_dir="D:\\drives\\transformers_cache\\cache\\")) 

# outlines prompt
@outlines.prompt
def replace_sensitive_info(text):
    """ 
    You are a data deanonymizer expert and assisting in this task. Your task is to identify and replace any sensitive information (names, emails, phone numbers and dates) in the given text with fake but realistic values. 
    In replacing names, you should use fake names of the same gender and of the same region, e.g you might replace jane with mary or pedro with luis.
   
    # EXAMPLE TEXT: 
    Contact Allan Mask email has allan.mask@example.com birth date 2021.12.25 and has phone number +358 409876541.
    
    # RESULT: 
    {
        "original": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "date": "1990.01.01",
            "Phone number": "+358 508765435"
        }
        "replacement":{
            "name": "Jim Jacks",
            "email": "jim.jacks@example.com",
            "date": "1991.02.03",
            "Phone number": "+358 409876541"
        }
    }
    # OUTPUT INSTRUCTIONS
    Answer in valid JSON. Here are the different objects relevant for the output:
    Anonymization: 
        original (dict): original sensitive information
        replacement (dict): fake but realistic values to replace teh original information

    # OUPUT TEXT:
    {{text}}
    # RESULT: 

    """
#
class Anonymization(BaseModel):
    original: Dict[str, str]
    replacement: Dict[str, str]

#
class DeAnonymization(BaseModel):
    text: str

@outlines.prompt
def deanonymize_text(text, mapping):
    """
    You are a data de-anonymization assistant. You task is to identify and replace any anonymized information in teh given text with the original text.
    # EXAMPLE TEXT: 
    {
        "given": {
            "name": "Jim Jacks",
            "email": "jim.jacks@example.com",
            "date": "1991.02.03",
            "Phone number": "+358 409876541"            
        }
        "original":{
            "name": "John Doe",
            "email": "john.doe@example.com",
            "date": "1990.01.01",
            "Phone number": "+358 508765435"
        }
    # RESULT: 
    Contact John Doe at john.doe@example.com by 2023-10-01.

    # OUTPUT INSTRUCTIONS:
    Answer in valid JSON. Here are the different objects relevant for the output.
    DeAnonymization: 
        text (str): de-anonymized text
    # OUTPUT TEXT: 
    {{ text }}

    # MAPPING: 
    {{ mappings}}
    # RESULTS:
    """
#
# original text
texts = ["Contact Jhon Doe email is john.doe@example.com by date 2023-10-01 and phone number +358 508765432.",
         "Contact Jane's email is jane.doe@example.com and her birthday date is 1992-05-15 and phone number +358 507659876."
        ]

prompts = [replace_sensitive_info(text) for text in texts]
generator = outlines.generate.json(model, Anonymization)
results = generator(prompts)

anonymized_texts = []

for text, result in zip(texts, results): 
    anonymized_text = text
    for key, value in result.original.items():
         if key in result.replacement:  
            anonymized_text = anonymized_text.replace(value, result.replacement[key])
    anonymized_texts.append(anonymized_text)

    print(f"\n Original text: {text}")
    print(f"\n Anonymized Text: {anonymized_texts}")
    print("\n" + "-"*40 + "\n")

# As local LLM to rephrase the text
text_generator = outlines.generate.text(model)
reworded_texts = []
for text in anonymized_texts:
    reworded_text = generator(f" rephrase this text: {text} ")
    reworded_texts.append(reworded_text)
    print(f"\n Rephrased text: {reworded_text}")

#
# Define de anonymization function using the mapping
def de_anonymize_text(anonymized_text, entity_mapping):
    given = entity_mapping['given']
    original = entity_mapping['original']
    text = str(anonymized_text)
    print("anonymized_text.text type: " + str(type(anonymized_text)))
    print("anonymized_text type: " + str(type(text)))
    keys = given.keys()
    for k in keys:
        fake_value =  given[k]
        if k in original:         
            real_value = original[k]
            print(text)
            print(f"\n key: {k} \t\t Fake Value: {fake_value} \t\t Real Value: {real_value}")
        
            text = text.replace(fake_value, real_value)
        else: 
            print (f"*** Error key: \t\t Value 1: {given[k]} \t\t Value2: *** NULL* ")

    return text

# De-anonymize each reworded text using the Phi-3 model ('model')
for text, anon_text, reworded_text, result in zip(texts, anonymized_texts, reworded_texts, results):
    mappings = {"given": result.replacement, "original": result.original}
    
    print(f"\nMappings: {mappings}\n")
    prompt = de_anonymize_text(reworded_text, mappings)
    # print (f"prompt is: {prompt} \n ####### \n")
    generator = outlines.generate.json(model, DeAnonymization)
    de_anonymized_result = generator([prompt])

    print(f"Initial prompt: {text}\n")
    print(f"Anonymized text: {anon_text}\n")
    print(f"Rewitten Response: {de_anonymized_result}\n")
    print("\n" + "-"*40 + "\n")
    print(f"")


