from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import AnalyzerEngine
from faker import Faker
from faker.providers import internet, person, date_time, phone_number
import csv
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, filename='anonymization.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Faker and Presidio engines
fake = Faker("en_US")
fake.add_provider(internet)
fake.add_provider(person)
fake.add_provider(date_time)
fake.add_provider(phone_number)

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

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
    "DATE_TIME": OperatorConfig("custom", {"lambda": fake_date_birth})
}

# Anonymize function
def anonymize_text(text):
    try:
        logger.info("Starting anonymization process.")
        analyzer_results = analyzer.analyze(text=text, language='en')
        anonymized_result = anonymizer.anonymize(text=text, analyzer_results=analyzer_results, operators=operators)
        logger.info("Anonymization completed successfully.")
        return anonymized_result.text, analyzer_results
    except Exception as e:
        logger.error(f"Error during anonymization: {str(e)}")
        return f"Error during anonymization: {str(e)}"

# De-anonymize function
def de_anonymize_text(anonymized_text, entity_mapping):
    try:
        logger.info("Starting de-anonymization process.")
        for fake_value, real_value in entity_mapping.items():
            anonymized_text = anonymized_text.replace(fake_value, str(real_value))
        logger.info("De-anonymization completed successfully.")
        return anonymized_text
    except Exception as e:
        logger.error(f"Error during de-anonymization: {str(e)}")
        return f"Error during de-anonymization: {str(e)}"

# Function to anonymize a CSV file
def anonymize_csv(input_csv, output_csv, mapping_file):
    try:
        logger.info(f"Anonymizing CSV file: {input_csv}")
        entity_mapping = {}
        with open(input_csv, newline='') as csvfile, open(output_csv, 'w', newline='') as outcsvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outcsvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                for field in fieldnames:
                    if row[field]:
                        anonymized_text, analyzer_results = anonymize_text(row[field])
                        row[field] = anonymized_text
                        for result in analyzer_results:
                            entity_mapping[result.start] = result.entity_type
                writer.writerow(row)

        with open(mapping_file, 'w') as mapfile:
            json.dump(entity_mapping, mapfile)
        logger.info(f"CSV file anonymized. Output written to: {output_csv}")
    except Exception as e:
        logger.error(f"Error during CSV anonymization: {str(e)}")
        return f"Error during CSV anonymization: {str(e)}"

# Function to de-anonymize a CSV file
def de_anonymize_csv(input_csv, output_csv, mapping_file):
    try:
        logger.info(f"De-anonymizing CSV file: {input_csv}")
        with open(mapping_file, 'r') as mapfile:
            entity_mapping = json.load(mapfile)

        with open(input_csv, newline='') as csvfile, open(output_csv, 'w', newline='') as outcsvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outcsvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                for field in fieldnames:
                    if row[field]:
                        row[field] = de_anonymize_text(row[field], entity_mapping)
                writer.writerow(row)
        logger.info(f"CSV file de-anonymized. Output written to: {output_csv}")
    except Exception as e:
        logger.error(f"Error during CSV de-anonymization: {str(e)}")
        return f"Error during CSV de-anonymization: {str(e)}"

if __name__ == "__main__":
    # Example usage
    choice = input("Enter 'anonymize' to anonymize data or 'deanonymize' to de-anonymize data: ").strip().lower()

    if choice == 'anonymize':
        sample_text = "John Doe was born on 1990-01-01. His email is john.doe@example.com and phone number is +1234567890."
        anonymized_text, analyzer_results = anonymize_text(sample_text)
        logger.info(f"Anonymized text: {anonymized_text}")

        # Example of anonymizing a CSV file
        anonymize_csv('input.csv', 'anonymized_output.csv', 'mapping.json')

    elif choice == 'deanonymize':
        entity_mapping = {
            fake_name(None): "John Doe",
            fake_phone_number(None): "+1234567890",
            fake_email(None): "john.doe@example.com",
            fake_date_birth(None): "1990-01-01"
        }
        anonymized_text = "John Doe was born on 1990-01-01. His email is john.doe@example.com and phone number is +1234567890."
        de_anonymized_text = de_anonymize_text(anonymized_text, entity_mapping)
        logger.info(f"De-anonymized text: {de_anonymized_text}")

        # Example of de-anonymizing a CSV file
        de_anonymize_csv('anonymized_output.csv', 'deanonymized_output.csv', 'mapping.json')
    else:
        print("Invalid choice. Please enter 'anonymize' or 'deanonymize'.")
