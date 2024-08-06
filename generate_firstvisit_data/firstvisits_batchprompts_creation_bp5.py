# Shaswato Sarker - TrustedAI

import json
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import time
import numpy as np

fake = Faker('fi_FI')  # Finnish locale

# Handcrafted examples for the prompt

examples = [
    {
        "Name": "Matti Virtanen",
        "SSN": "010180-123A",
        "Address": "Pihlajatie 1, 00100 Helsinki",
        "Condition": "diabetes",
        "Age": 45,
        "Report": """
        Patient Information:
        - Name: Matti Virtanen
        - Personal Identity Code: 010180-123A
        - Age: 45 years old
        - Address: Pihlajatie 1, 00100 Helsinki

        Medical History:
        The patient sought treatment due to diabetes and symptoms of high blood sugar and increased thirst that started two weeks ago.

        Vital Signs:
        - Blood Pressure: 130/80 mmHg
        - Pulse: 72/min
        - SpO2: 97%

        Neurological Status: No foci

        Procedure & Medication:
        Prescribed Metformin 500 mg twice daily to manage blood sugar levels. Advised to monitor blood sugar levels regularly.

        Follow Up:
        The patient was instructed to monitor symptoms and return to the clinic in a week if there is no improvement.
        """
    },
    {
        "Name": "Laura Korhonen",
        "SSN": "150488-456B",
        "Address": "Tammitie 3, 00500 Helsinki",
        "Condition": "asthma",
        "Age": 32,
        "Report": """
        Patient Profile:
        - Name: Laura Korhonen
        - Personal Identity Code: 150488-456B
        - Age: 32 years old
        - Address: Tammitie 3, 00500 Helsinki

        Medical History:
        The patient sought treatment due to asthma and symptoms of shortness of breath and wheezing that started a week ago.

        Vital Signs:
        - Blood Pressure: 120/75 mmHg
        - Pulse: 80/min
        - SpO2: 95%

        Neurological Status: No foci

        Procedure & Medication:
        Prescribed Salbutamol inhaler for immediate relief and advised to use as needed.

        Follow Up:
        The patient was instructed to monitor symptoms and return to the clinic in a week if there is no improvement.
        """
    },
    {
        "Name": "Pekka Nieminen",
        "SSN": "240960-789C",
        "Address": "Koivukuja 7, 00700 Helsinki",
        "Condition": "hypertension",
        "Age": 60,
        "Report": """
        Summary:
        Patient Details:
        - Name: Pekka Nieminen
        - Personal Identity Code: 240960-789C
        - Age: 60 years old
        - Address: Koivukuja 7, 00700 Helsinki

        Medical History:
        The patient sought treatment due to hypertension and symptoms of headache and chest pain that started a month ago.

        Vital Signs:
        - Blood Pressure: 150/95 mmHg
        - Pulse: 75/min
        - SpO2: 96%

        Neurological Status: No foci

        Procedure & Medication:
        Prescribed Amlodipine 5 mg once daily to manage blood pressure. Advised to reduce salt intake and exercise regularly.

        Follow Up:
        The patient was instructed to monitor symptoms and return to the clinic in a week if there is no improvement.
        """
    },
    {
        "Name": "Antti Mäkelä",
        "SSN": "300691-987D",
        "Address": "Koivuhaantie 9, 00930 Helsinki",
        "Condition": "chronic cephalgia",
        "Age": 33,
        "Report": """
        Patient Information Summary:
        - Name: Antti Mäkelä
        - Personal Identity Code: 300691-987D
        - Age: 33 years old
        - Address: Koivuhaantie 9, 00930 Helsinki

        Medical History:
        The patient sought treatment due to chronic cephalgia and symptoms of headache and sensitivity to light that started three weeks ago.

        Vital Signs:
        - Blood Pressure: 125/80 mmHg
        - Pulse: 70/min
        - SpO2: 98%

        Neurological Status: No foci

        Procedure & Medication:
        Prescribed Paracetamol 1g three times a day as needed for pain management. Advised to avoid bright lights.

        Follow Up:
        The patient was instructed to monitor symptoms and return to the clinic in a week if there is no improvement.
        """
    },
    {
        "Name": "Sari Lehtinen",
        "SSN": "220570-567E",
        "Address": "Lehtikuusentie 5, 00300 Espoo",
        "Condition": "vertigo",
        "Age": 54,
        "Report": """
        Patient Profile:
        - Name: Sari Lehtinen
        - Personal Identity Code: 220570-567E
        - Age: 54 years old
        - Address: Lehtikuusentie 5, 00300 Espoo

        Medical History:
        The patient sought treatment due to vertigo and symptoms of dizziness and balance issues that started a week ago.

        Vital Signs:
        - Blood Pressure: 115/75 mmHg
        - Pulse: 68/min
        - SpO2: 99%

        Neurological Status: No foci

        Procedure & Medication:
        Prescribed Betahistine 16 mg three times a day. Advised to avoid sudden head movements.

        Follow Up:
        The patient was instructed to monitor symptoms and return to the clinic in a week if there is no improvement.
        """
    },
    {
        "Name": "Eero Virtanen",
        "SSN": "010123-111N",
        "Address": "Vauvakatu 1, 00100 Helsinki",
        "Condition": "neonatal jaundice",
        "Age": 0.02,  # ~7 days
        "Report": """
        Patient Information:
        - Name: Eero Virtanen
        - Personal Identity Code: 010123-111N
        - Age: 7 days old
        - Address: Vauvakatu 1, 00100 Helsinki

        Medical History:
        The newborn was brought in due to yellowing of the skin and eyes, indicating possible neonatal jaundice.

        Vital Signs:
        - Temperature: 36.8°C
        - Heart Rate: 130/min
        - Respiratory Rate: 45/min

        Neurological Status: Alert and responsive

        Procedure & Medication:
        Initiated phototherapy treatment. Encouraged frequent breastfeeding to help clear bilirubin.

        Follow Up:
        Parents instructed to return in 24 hours for bilirubin level check.
        """
    },
    {
        "Name": "Aino Korhonen",
        "SSN": "250123-222N",
        "Address": "Vauvatie 2, 00200 Helsinki",
        "Condition": "feeding difficulties",
        "Age": 0.06,  # ~22 days
        "Report": """
        Patient Profile:
        - Name: Aino Korhonen
        - Personal Identity Code: 250123-222N
        - Age: 22 days old
        - Address: Vauvatie 2, 00200 Helsinki

        Medical History:
        Parents brought the newborn due to difficulties with breastfeeding and concerns about weight gain.

        Vital Signs:
        - Temperature: 36.5°C
        - Heart Rate: 125/min
        - Respiratory Rate: 40/min

        Neurological Status: Alert, good muscle tone

        Procedure & Medication:
        Performed physical examination and weight check. Provided lactation consultation and demonstrated proper breastfeeding techniques.

        Follow Up:
        Scheduled for weight check and feeding assessment in 3 days.
        """
    },
    # Infants (I)
    {
        "Name": "Onni Mäkinen",
        "SSN": "010622-333I",
        "Address": "Taaperokuja 3, 00300 Helsinki",
        "Condition": "ear infection",
        "Age": 0.75,  # 9 months
        "Report": """
        Patient Information:
        - Name: Onni Mäkinen
        - Personal Identity Code: 010622-333I
        - Age: 9 months old
        - Address: Taaperokuja 3, 00300 Helsinki

        Medical History:
        Brought in by parents due to fever, irritability, and pulling at right ear for the past 24 hours.

        Vital Signs:
        - Temperature: 38.2°C
        - Heart Rate: 120/min
        - Respiratory Rate: 30/min

        Neurological Status: Irritable but consolable

        Procedure & Medication:
        Diagnosed with acute otitis media. Prescribed amoxicillin suspension, 90mg/kg/day divided every 12 hours for 10 days.

        Follow Up:
        Return in 48-72 hours if symptoms worsen or fever persists. Otherwise, follow-up in 10 days.
        """
    },
    {
        "Name": "Emilia Laine",
        "SSN": "151021-444I",
        "Address": "Vauvakatu 4, 00400 Helsinki",
        "Condition": "bronchiolitis",
        "Age": 0.33,  # 4 months
        "Report": """
        Summary:
        Patient Details:
        - Name: Emilia Laine
        - Personal Identity Code: 151021-444I
        - Age: 4 months old
        - Address: Vauvakatu 4, 00400 Helsinki

        Medical History:
        Presented with cough, wheezing, and difficulty feeding for the past 2 days.

        Vital Signs:
        - Temperature: 37.8°C
        - Heart Rate: 140/min
        - Respiratory Rate: 50/min
        - SpO2: 94% on room air

        Neurological Status: Alert but fussy

        Procedure & Medication:
        Diagnosed with bronchiolitis. Administered nebulized saline and provided nasal suctioning. Educated parents on home management including hydration and nasal suctioning.

        Follow Up:
        Return immediately if breathing difficulties increase or feeding decreases significantly. Otherwise, follow-up in 2-3 days.
        """
    },
    # Toddlers and Preschoolers (T)
    {
        "Name": "Eino Järvinen",
        "SSN": "010319-555T",
        "Address": "Leikkikatu 5, 00500 Helsinki",
        "Condition": "chickenpox",
        "Age": 3,
        "Report": """
        Patient Information Summary:
        - Name: Eino Järvinen
        - Personal Identity Code: 010319-555T
        - Age: 3 years old
        - Address: Leikkikatu 5, 00500 Helsinki

        Medical History:
        Brought in by parents due to fever and itchy rash that started yesterday.

        Vital Signs:
        - Temperature: 38.5°C
        - Heart Rate: 110/min
        - Respiratory Rate: 24/min

        Neurological Status: Alert and interactive

        Procedure & Medication:
        Diagnosed with chickenpox. Prescribed calamine lotion for itching and acetaminophen for fever. Advised on preventing scratch complications.

        Follow Up:
        Keep isolated until lesions crust over. Return if high fever persists or new symptoms develop.
        """
    },
    {
        "Name": "Sofia Nieminen",
        "SSN": "250920-666T",
        "Address": "Päiväkotitie 6, 00600 Helsinki",
        "Condition": "allergic reaction",
        "Age": 4,
        "Report": """
        Patient Profile:
        - Name: Sofia Nieminen
        - Personal Identity Code: 250920-666T
        - Age: 4 years old
        - Address: Päiväkotitie 6, 00600 Helsinki

        Medical History:
        Rushed in by parents after developing hives and facial swelling following peanut ingestion.

        Vital Signs:
        - Temperature: 37.0°C
        - Heart Rate: 100/min
        - Respiratory Rate: 22/min
        - SpO2: 98%

        Neurological Status: Alert, no respiratory distress

        Procedure & Medication:
        Administered oral antihistamine. Prescribed EpiPen for future emergencies and educated parents on its use. Referred to allergist for further evaluation.

        Follow Up:
        Avoid all peanut products. Follow up with allergist within 2 weeks. Return immediately if any sign of respiratory distress or recurrence of symptoms.
        """
    },
    # School-Age Children (S)
    {
        "Name": "Mikko Koskinen",
        "SSN": "010714-777S",
        "Address": "Koululaiskatu 7, 00700 Helsinki",
        "Condition": "appendicitis",
        "Age": 9,
        "Report": """
        Patient Information:
        - Name: Mikko Koskinen
        - Personal Identity Code: 010714-777S
        - Age: 9 years old
        - Address: Koululaiskatu 7, 00700 Helsinki

        Medical History:
        Presented with right lower quadrant pain, nausea, and low-grade fever for the past 24 hours.

        Vital Signs:
        - Temperature: 38.0°C
        - Heart Rate: 90/min
        - Blood Pressure: 110/70 mmHg
        - SpO2: 99%

        Neurological Status: Alert and oriented

        Procedure & Medication:
        Diagnosed with acute appendicitis based on physical exam and ultrasound findings. Admitted for emergency appendectomy.

        Follow Up:
        Post-operative follow-up in 1 week. Parents instructed on wound care and to return if fever or increased pain occurs.
        """
    },
    {
        "Name": "Ella Vuorinen",
        "SSN": "151215-888S",
        "Address": "Opintotie 8, 00800 Helsinki",
        "Condition": "type 1 diabetes",
        "Age": 11,
        "Report": """
        Summary:
        Patient Details:
        - Name: Ella Vuorinen
        - Personal Identity Code: 151215-888S
        - Age: 11 years old
        - Address: Opintotie 8, 00800 Helsinki

        Medical History:
        Brought in due to increased thirst, frequent urination, and weight loss over the past month.

        Vital Signs:
        - Temperature: 36.8°C
        - Heart Rate: 88/min
        - Blood Pressure: 105/65 mmHg
        - Blood Glucose: 320 mg/dL

        Neurological Status: Alert and oriented

        Procedure & Medication:
        Diagnosed with Type 1 Diabetes. Initiated on insulin therapy. Provided diabetes education including blood glucose monitoring and insulin administration.

        Follow Up:
        Follow-up with pediatric endocrinologist in 3 days. Parents and patient instructed on signs of hypo- and hyperglycemia, and when to seek immediate medical attention.
        """
    },
    # Adolescents (A)
    {
        "Name": "Leevi Saarinen",
        "SSN": "010505-999A",
        "Address": "Teini-ikäkatu 9, 00900 Helsinki",
        "Condition": "sports injury",
        "Age": 16,
        "Report": """
        Patient Information:
        - Name: Leevi Saarinen
        - Personal Identity Code: 010505-999A
        - Age: 16 years old
        - Address: Teini-ikäkatu 9, 00900 Helsinki

        Medical History:
        Presented with left ankle pain and swelling after a basketball game injury.

        Vital Signs:
        - Temperature: 37.0°C
        - Heart Rate: 72/min
        - Blood Pressure: 120/80 mmHg

        Neurological Status: Alert and oriented

        Procedure & Medication:
        X-ray showed no fracture. Diagnosed with grade 2 ankle sprain. Applied RICE protocol (Rest, Ice, Compression, Elevation). Prescribed NSAIDs for pain and swelling.

        Follow Up:
        Follow-up in 1 week. Advised to use crutches and avoid weight-bearing for 48 hours. Provided instructions for gradual return to activities and physical therapy exercises.
        """
    },
    {
        "Name": "Iida Heikkinen",
        "SSN": "150704-000A",
        "Address": "Nuorisotie 10, 01000 Helsinki",
        "Condition": "depression",
        "Age": 17,
        "Report": """
        Patient Profile:
        - Name: Iida Heikkinen
        - Personal Identity Code: 150704-000A
        - Age: 17 years old
        - Address: Nuorisotie 10, 01000 Helsinki

        Medical History:
        Self-referred due to persistent feelings of sadness, loss of interest in activities, and difficulty concentrating for the past 3 months.

        Vital Signs:
        - Temperature: 36.7°C
        - Heart Rate: 76/min
        - Blood Pressure: 115/75 mmHg

        Neurological Status: Alert, oriented, affect flat

        Procedure & Medication:
        Diagnosed with Major Depressive Disorder based on DSM-5 criteria. Initiated on Fluoxetine 10mg daily. Referred for cognitive behavioral therapy.

        Follow Up:
        Follow-up in 2 weeks to assess medication response and side effects. Provided crisis hotline information and safety plan. Parents educated on warning signs and supportive strategies.
        """
    }
]

def select_age_group():
    age_groups = [
        ("N", 0, 28/365),  # Neonates: 0-28 days
        ("I", 29/365, 1),  # Infants: 1 month to 1 year
        ("T", 1, 5),       # Toddlers and Preschoolers
        ("S", 6, 12),      # School-Age Children
        ("A", 13, 18),     # Adolescents
        ("D", 19, 64),     # Adults
        ("E", 65, 100)     # Elderly
    ]
    weights = [5, 5, 10, 10, 15, 40, 15]  # Probability distribution (in percentage)
    cumulative_weights = [sum(weights[:i+1]) for i in range(len(weights))]
    
    random_value = random.uniform(0, 100)
    for i, threshold in enumerate(cumulative_weights):
        if random_value <= threshold:
            return age_groups[i]

def select_age_from_age_group(age_group):
    group, min_age, max_age = age_group
    
    if group == "N":
        return random.randint(0, 28) / 365  # 0-28 days in years
    elif group == "I":
        return random.randint(29, 365) / 365  # 29-365 days in years
    elif group in ["T", "S", "A"]:
        # For younger age groups, use uniform distribution
        return random.uniform(min_age, max_age)
    elif group == "D":
        # For adults, use a beta distribution to favor middle ages
        return min_age + (max_age - min_age) * np.random.beta(2, 2)
    elif group == "E":
        # For elderly, use a beta distribution to favor younger elderly
        return min_age + (max_age - min_age) * np.random.beta(1.5, 3)

def load_conditions(conditions_filepath):
    conditions = []
    with open(conditions_filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('|')
                if len(parts) == 3:
                    condition, age_probs, gender = parts
                    age_probs = dict(zip(['N', 'I', 'T', 'S', 'A', 'D', 'E'], map(int, age_probs.split(',')[0].split(',')[1:])))
                    conditions.append({
                        'name': condition.strip(),
                        'age_probs': age_probs,
                        'gender': gender.strip()
                    })
    return conditions

def select_condition(age_group, gender, conditions):
    eligible_conditions = []
    for condition in conditions:
        if condition['gender'] in [gender, 'B']:
            prob = condition['age_probs'].get(age_group, 0)  # Use get() with default value 0
            if prob > 0:
                eligible_conditions.extend([condition['name']] * prob)
    return random.choice(eligible_conditions) if eligible_conditions else "General check-up"

def get_age_group(age):
    if age < 28/365:
        return "N"
    elif age < 1:
        return "I"
    elif age < 5:
        return "T"
    elif age < 12:
        return "S"
    elif age < 18:
        return "A"
    elif age < 65:
        return "D"
    else:
        return "E"

def select_random_examples(examples, patient_age_group, patient_gender, n=2):
    # Filter examples by age group and gender
    appropriate_examples = [ex for ex in examples if get_age_group(ex["Age"]) == patient_age_group]
    
    if len(appropriate_examples) < n:
        # If not enough examples in the same age group, include adjacent age groups
        adjacent_groups = {
            "N": ["I"],
            "I": ["N", "T"],
            "T": ["I", "S"],
            "S": ["T", "A"],
            "A": ["S", "D"],
            "D": ["A", "E"],
            "E": ["D"]
        }
        for adj_group in adjacent_groups[patient_age_group]:
            appropriate_examples.extend([ex for ex in examples if get_age_group(ex["Age"]) == adj_group])
    
    # Ensure gender balance
    male_examples = [ex for ex in appropriate_examples if ex.get("Gender", "Male") == "Male"]
    female_examples = [ex for ex in appropriate_examples if ex.get("Gender", "Female") == "Female"]
    
    if patient_gender == "Male":
        selected = random.sample(male_examples, min(1, len(male_examples)))
        if len(selected) < n:
            selected.extend(random.sample(female_examples, min(n - len(selected), len(female_examples))))
    else:
        selected = random.sample(female_examples, min(1, len(female_examples)))
        if len(selected) < n:
            selected.extend(random.sample(male_examples, min(n - len(selected), len(male_examples))))
    
    # If we still don't have enough examples, pad with random selections
    if len(selected) < n:
        selected.extend(random.sample(examples, n - len(selected)))
    
    return selected[:n]

def generate_initial_context(selected_examples):
    example_reports = "\n".join([ex["Report"] for ex in selected_examples])
    initial_context_messages = [
        {"role": "system", "content": "You are a healthcare professional who often uses an advanced clinical language model that can analyze medical data to generate medical reports."},
        {"role": "user", "content": f"""
        Let's suppose you want to generate a report on a patient with the following information:

        Example Reports:
        {example_reports}

        For this, you must ensure the report includes the medical history, vital signs, neurological status, procedure & medication, and follow-up instructions. The report should be relevant to the patient's condition, age, and gender.
        We also offer some example reports for your reference. Although you can refer to these examples, try to create a distinct report, using the examples only as inspiration. 
        Also, try to keep the reports as brief and straightforward as possible.
        Pay close attention to age-appropriate and gender-specific medical concerns, treatments, and language when generating the report.
        """}
    ]
    return initial_context_messages

def generate_prompt(name, ssn, address, age, gender, condition):
    prompt = f"""
    Patient Information:
    - Name: {name}
    - Personal Identity Code: {ssn}
    - Age: {age:.2f}
    - Gender: {gender}
    - Address: {address}
    - Condition: {condition}

    Please generate a medically consistent report similar to the examples provided in the initial context, with the report pertinent to the patient's condition, age group, and gender.
    Consider any specific health concerns or screenings that may be relevant to the patient.
    """
    return prompt

def generate_batch_prompts(num_records, conditions):
    batch_prompts = []

    for i in range(num_records):
        name = fake.name()
        ssn = fake.ssn()
        address = fake.address().replace('\n', ', ')
        age_group, min_age, max_age = select_age_group()
        age = select_age_from_age_group((age_group, min_age, max_age))
        gender = random.choice(['Male', 'Female'])
        condition = select_condition(age_group, gender[0], conditions)

        selected_examples = select_random_examples(examples, age_group, gender, n=2)
        initial_context_messages = generate_initial_context(selected_examples)
        prompt = generate_prompt(name, ssn, address, age, gender, condition)

        batch_prompt = {
            "custom_id": f"request-{i+1}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini-2024-07-18",
                "messages": initial_context_messages + [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            }
        }
        batch_prompts.append(batch_prompt)

    return batch_prompts

def save_batch_prompts(batch_prompts, output_directory, filename):
    os.makedirs(output_directory, exist_ok=True)
    filepath = os.path.join(output_directory, filename)
    with open(filepath, 'w') as f:
        for prompt in batch_prompts:
            f.write(json.dumps(prompt) + '\n')
    print(f"Batch prompts saved to {filepath}")

def main(num_files, num_records, conditions_filepath, output_directory):
    conditions = load_conditions(conditions_filepath)
    
    for i in range(num_files):
        batch_prompts = generate_batch_prompts(num_records, conditions)
        
        timestamp = (datetime.now() + timedelta(seconds=i)).strftime("%Y%m%d_%H%M%S")
        filename = f'batch_prompts_{timestamp}.jsonl'
        
        save_batch_prompts(batch_prompts, output_directory, filename)
        
        time.sleep(1)

    print(f"Created {num_files} files, each with {num_records} records.")

if __name__ == "__main__":
    num_files = 20
    num_records = 1000
    conditions_filepath = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\data\medical_conditions.txt'
    output_directory = r'C:\Users\galaxy\Documents\VsCode\CodeTrustedAI\files\input'

    main(num_files, num_records, conditions_filepath, output_directory)






