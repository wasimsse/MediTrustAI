from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import AnalyzerEngine
from faker import Faker
from faker.providers import internet, person, date_time, phone_number
import logging

# Initialize Faker and Presidio engines
fake = Faker("en_US")
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(phone_number)

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define custom Faker functions
def fake_name(x):
    Faker.seed(42)
    return fake.name()

def fake_phone_number(x):
    Faker.seed(42)
    return fake.phone_number()

def fake_email(x):
    Faker.seed(42)
    return fake.ascii_email()

def fake_date_birth(x):
    Faker.seed(42)
    return fake.date_of_birth().isoformat()

# Define custom operators
operators = {
    "PERSON": OperatorConfig("custom", {"lambda": fake_name}),
    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_phone_number}),
    "EMAIL": OperatorConfig("custom", {"lambda": fake_email}),
    "DATE_OF_BIRTH": OperatorConfig("custom", {"lambda": fake_date_birth})
}

# Anonymize function
def anonymize_text(text):
    """
    Anonymizes the provided text using Presidio and Faker.

    Args:
        text (str): The text to anonymize.

    Returns:
        str: Anonymized text.
        list: Analysis results from Presidio.
    """
    try:
        analyzer_results = analyzer.analyze(text=text, language='en')
        anonymized_result = anonymizer.anonymize(text=text, analyzer_results=analyzer_results, operators=operators)
        return anonymized_result.text, analyzer_results
    except Exception as e:
        logger.error(f"An error occurred during anonymization: {str(e)}")
        return None, None

# De-anonymize function
def de_anonymize_text(anonymized_text, entity_mapping):
    """
    De-anonymizes the provided text using the provided entity mapping.

    Args:
        anonymized_text (str): The text to de-anonymize.
        entity_mapping (dict): A dictionary mapping fake values to real values.

    Returns:
        str: De-anonymized text.
    """
    try:
        for fake_value, real_value in entity_mapping.items():
            anonymized_text = anonymized_text.replace(fake_value, str(real_value))
        return anonymized_text
    except Exception as e:
        logger.error(f"An error occurred during de-anonymization: {str(e)}")
        return None
