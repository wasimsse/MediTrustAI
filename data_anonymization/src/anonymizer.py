# data_anonymization/src/anonymizer.py

from faker_anonymizer import anonymize_text, de_anonymize_text, fake_name, fake_phone_number, fake_email, fake_date_birth

# Example usage of the anonymize and de-anonymize functions
def main():
    text = "Allan Mask's email address is allan.mask@example.com, birthdate is 2021.12.25, and phone number is +358 409876541."

    # Anonymize the text
    anonymized_text, analyzer_results = anonymize_text(text)
    
    # Example entity mapping for de-anonymization
    entity_mapping = {
        fake_name(None): "Allan Mask",
        fake_phone_number(None): "+358 409876541",
        fake_email(None): "allan.mask@example.com",
        fake_date_birth(None): "2021-12-25"
    }

    # De-anonymize the text
    de_anonymized_text = de_anonymize_text(anonymized_text, entity_mapping)

    # Print results to console
    print(f"Original text: {text}")
    print(f"Anonymized text: {anonymized_text}")
    print(f"De-anonymized text: {de_anonymized_text}")

    # Write results to a file
    with open("output.txt", "w") as f:
        f.write(f"Original text: {text}\n")
        f.write(f"Anonymized text: {anonymized_text}\n")
        f.write(f"De-anonymized text: {de_anonymized_text}\n")

if __name__ == "__main__":
    main()
