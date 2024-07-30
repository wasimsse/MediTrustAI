
#  conda activate py312_data_anonymizing  

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult
from presidio_analyzer import AnalyzerEngine
from faker import Faker
from faker.providers import internet, person, date_time, phone_number

from presidio_anonymizer.entities import OperatorConfig

engine = AnonymizerEngine()
# This will use a large spacy model by default: en_core_web_lg
# setup teh engine, loads NLP module (spaCy model by default) and other PII recognizers 
analyzer = AnalyzerEngine()

fake = Faker("en_US")
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(phone_number)

prompt2 = " Allan Mask email address is allan.mask@example.com, birthdate is 2021.12.25 has phone number +358 409876541."
prompt2_analyzer_result = analyzer.analyze(text=prompt2, language='en')

print(f"\n\n Analyzer results: {prompt2_analyzer_result} ")

def fake_name(x):
    Faker.seed(42) # just to get same name for debugging, do not use it in production.
    return fake.name()

def fake_phone_number(x):
    Faker.seed(42) # just to get same name for debugging, do not use it in production.
    return fake.phone_number()

def fake_email(x):
    Faker.seed(42) # just to get same name for debugging, do not use it in production.
    return fake.ascii_email()

def fake_date_birth(x):
    Faker.seed(42) # just to get same name for debugging, do not use it in production.
    return fake.date_of_birth()

# Create custom operator for PERSON entity
operators = {"PERSON": OperatorConfig("custom", {"lambda": fake_name}),
             "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone_number}),
             "EMAIL": OperatorConfig("custom", {"lambda": fake_email}),
             "DATE_OF_BIRTH": OperatorConfig("custom", {"lambda": fake_date_birth})
             }
#invoke teh anonymize funtion with the text
# Operators to get the anonymization output:
prompt2_anon_result = engine.anonymize(text=prompt2, analyzer_results=prompt2_analyzer_result, operators=operators)

print(f"\n\n Original text: {prompt2}")
print(f"\n\n anonymize2 results: {prompt2_anon_result.text}")

# anonymize the text with analyzer results
def anonymize_text(analyzer_results, text_to_anonymize):
    """ Anonymize text using Faker and build a mapping for de-anonymization. """
    entity_mapping = {}
    updated_text = text_to_anonymize # use updated_text to avoid modifing the original text
    def replace_and_store(entity_type, replacement_func): 
            nonlocal updated_text # Reference the non-local varibale
            for result in analyzer_results:
                 if result.entity_type == entity_type: 
                      original_value = text_to_anonymize[result.start:result.end]
                      fake_value = replacement_func()
                      entity_mapping[fake_value] = original_value
                      # replce in the updated_text the real value with fake value
                      updated_text = updated_text.replace(original_value, fake_value, 1)
            return updated_text
    
    updated_text = replace_and_store("EMAIL_ADDRESS", fake.safe_email)
    updated_text = replace_and_store("PERSON", fake.name)
    updated_text = replace_and_store("DATE_TIME", lambda: fake.date_time().strftime('%y-%m-%d'))

    return updated_text, entity_mapping

#Define de anonymization function using the mapping
def de_anonymize_text(anonymized_text, entity_mapping):
    for fake_value, real_value in entity_mapping():
        anonymized_text = anonymized_text.replace(fake_value, real_value)

    return anonymized_text

# Analyze the text
# Note that the supported entities are listed https://microsoft.github.io/presidio/supported_entities/
# Entity detection cam involve multiple techniques - including regex, SpaCy model (For context), 
# Checksums (validating credit card numbers)
analyzer_results2 = analyzer.analyze(text=prompt2, entities=["EMAIL_ADDRESS", "PERSON", "DATE_TIME"], language="en")

print(f"\n\n Original Text: \n{prompt2}")
print(f"\n\n Analyzer Results: \n{analyzer_results2}")

# Anonymize the text and analysis results
anonymized_text2, entity_mapping2 = anonymize_text(analyzer_results2, prompt2)
print(f"\n\n method 2 anonymized text\n{anonymized_text2}")
print(f"\n\n Entity Mapping\n{entity_mapping2}")

# TODO check fuzzy matching (to grab slight mis-spellings)
# TODO check Langchain has wrapper for reversable presidio
# https://python.langchain.com/v0.1/docs/guides/productionization/safety/presidio_data_anonymization/reversible/
# https://python.langchain.com/v0.1/docs/guides/productionization/safety/presidio_data_anonymization/reversible/
# 

