import random
from collections import deque

def current_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no medications prescribed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures performed" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"The following procedures were performed: {row['Procedures'].lower()}."

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"This is the {visit_count_str} visit for patient {row['Name']} (ID: {row['PatientID']}), a {row['Age']}-year-old {row['Gender']} "
        f"from {row['Address']}. The patient has a history of {row['InitialCondition']}. In addition, they have been diagnosed with "
        f"the following long-term conditions: {row['LongTermConditions'].lower()} and secondary conditions including {row['SecondaryConditions'].lower()}. "
        f"The patient has {allergies_str}. "
        f"During this visit on {row['VisitDate']}, which is a {row['VisitType']}, they reported the following symptoms: {symptoms_str} "
        f"Vital signs recorded were: blood pressure {row['BloodPressure']}, pulse {row['Pulse']} bpm, oxygen saturation (SpO2) at {row['SpO2']}, "
        f"body temperature at {row['Temperature']}°C, weight {row['Weight']} kg, and height {row['Height']} cm. "
        f"The diagnosis for this visit is {row['Diagnosis'].lower()}. The patient has been {medication_str}. "
        f"Lab results indicate {lab_results_str} {procedures_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f" During the last visit on {previous_visit_date}, the patient reported {previous_symptoms} "
            f"The diagnosis at that time was {previous_diagnosis}. They were {previous_medication}, "
            f"and lab results showed {previous_lab_results} The medical note from that visit was: {previous_medical_notes}."
        )
    
    return user_message.replace('..', '.').strip()

def narrative_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no medications prescribed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures were necessary" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"the following procedures were carried out: {row['Procedures'].lower()}."

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Today, we're seeing {row['Name']} (Patient ID: {row['PatientID']}) for their {visit_count_str} visit. {row['Name']} is a {row['Age']}-year-old {row['Gender']} "
        f"who resides at {row['Address']}. Looking at their medical history, we see that {row['Name']} has a history of {row['InitialCondition']}. "
        f"Over time, they've also been diagnosed with some long-term conditions, namely {row['LongTermConditions'].lower()}. Additionally, "
        f"they have some secondary conditions to keep in mind: {row['SecondaryConditions'].lower()}. It's worth noting that the patient has {allergies_str}. "
        f"Now, focusing on today's visit on {row['VisitDate']}, which is categorized as a {row['VisitType']}, {row['Name']} came in reporting the following symptoms: {symptoms_str} "
        f"We took their vital signs, and here's what we found: their blood pressure was {row['BloodPressure']}, pulse was {row['Pulse']} beats per minute, "
        f"oxygen saturation (SpO2) was at {row['SpO2']}, body temperature was {row['Temperature']}°C, they weighed in at {row['Weight']} kg, and their height was recorded as {row['Height']} cm. "
        f"After examination, our diagnosis for this visit is {row['Diagnosis'].lower()}. In terms of treatment, the patient has been {medication_str}. "
        f"We also ran some lab tests, and the results indicate {lab_results_str} As for procedures, {procedures_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications were prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"they were prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f" It's important to note that during their last visit on {previous_visit_date}, {row['Name']} reported {previous_symptoms} "
            f"At that time, our diagnosis was {previous_diagnosis}. Regarding treatment, {previous_medication}. "
            f"The lab results from that visit showed {previous_lab_results} For completeness, here's a note from that visit: {previous_medical_notes}."
        )
    
    return user_message.replace('..', '.').strip()

def conversational_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "doesn't have any known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"is allergic to {row['Allergies'].lower()}"
    medication_str = "hasn't been prescribed any medications" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"has been prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "we didn't need to perform any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we performed the following procedures: {row['Procedures'].lower()}."

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Hey there! I've just finished seeing {row['Name']} - you know, the patient with ID {row['PatientID']}. This was their {visit_count_str} visit with us. "
        f"Just to refresh your memory, {row['Name']} is a {row['Age']}-year-old {row['Gender']} living at {row['Address']}. "
        f"Now, as you probably remember, they've got a history of {row['InitialCondition']}. On top of that, they've been dealing with "
        f"some long-term conditions: {row['LongTermConditions'].lower()}. Oh, and we shouldn't forget about these secondary conditions: {row['SecondaryConditions'].lower()}. "
        f"By the way, the patient {allergies_str}. "
        f"So, about today's visit on {row['VisitDate']} - it was a {row['VisitType']}. {row['Name']} came in telling me about these symptoms: {symptoms_str} "
        f"I checked their vitals, and here's what I got: blood pressure was {row['BloodPressure']}, pulse was running at {row['Pulse']} bpm, "
        f"their oxygen saturation was sitting at {row['SpO2']}, body temp was {row['Temperature']}°C, they weighed in at {row['Weight']} kg, and stood at {row['Height']} cm. "
        f"After looking everything over, I've diagnosed them with {row['Diagnosis'].lower()}. As for treatment, the patient {medication_str}. "
        f"We ran some labs, and the results are showing {lab_results_str} Oh, and as for procedures, {procedures_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "they weren't prescribed any medications" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"they were put on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f" Oh, I almost forgot! When {row['Name']} was here last time on {previous_visit_date}, they mentioned {previous_symptoms} "
            f"Back then, we thought it was {previous_diagnosis}. For treatment, {previous_medication}. "
            f"The labs from that visit came back showing {previous_lab_results} And just to jog your memory, here's what I noted down after that visit: {previous_medical_notes}."
        )
    
    return user_message.replace('..', '.').strip()

def detailed_clinical_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "No known allergies (NKA)" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"Allergies: {row['Allergies'].lower()}"
    medication_str = "No medications prescribed at this time" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"Medications prescribed: {row['MedicationPrescribed'].lower()}"
    procedures_str = "No procedures performed during this visit" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"Procedures performed: {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Clinical Note - Visit {visit_count_str}\n\n"
        f"Patient: {row['Name']} (ID: {row['PatientID']})\n"
        f"Demographics: {row['Age']}-year-old {row['Gender']}, residing at {row['Address']}\n\n"
        f"Medical History:\n"
        f"- Primary condition: {row['InitialCondition']}\n"
        f"- Chronic conditions: {row['LongTermConditions'].lower()}\n"
        f"- Secondary conditions: {row['SecondaryConditions'].lower()}\n"
        f"- {allergies_str}\n\n"
        f"Current Visit ({row['VisitDate']}) - {row['VisitType']}:\n"
        f"Chief complaint: Patient presents with {symptoms_str}\n\n"
        f"Vital Signs:\n"
        f"- Blood Pressure: {row['BloodPressure']}\n"
        f"- Pulse: {row['Pulse']} bpm\n"
        f"- SpO2: {row['SpO2']}\n"
        f"- Temperature: {row['Temperature']}°C\n"
        f"- Weight: {row['Weight']} kg\n"
        f"- Height: {row['Height']} cm\n\n"
        f"Assessment: {row['Diagnosis'].lower()}\n\n"
        f"Plan:\n"
        f"1. {medication_str}\n"
        f"2. {procedures_str}\n"
        f"3. Laboratory studies: {lab_results_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "No medications were prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"Medications prescribed: {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nPrevious Visit Summary ({previous_visit_date}):\n"
            f"- Presenting symptoms: {previous_symptoms}\n"
            f"- Diagnosis: {previous_diagnosis}\n"
            f"- Treatment: {previous_medication}\n"
            f"- Laboratory findings: {previous_lab_results}\n"
            f"- Clinical notes: {previous_medical_notes}"
        )
    
    return user_message.replace('..', '.').strip()

def empathetic_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "doesn't have any known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"has allergies to {row['Allergies'].lower()}"
    medication_str = "doesn't need any new medications at this time" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"has been prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "didn't require any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"underwent the following procedures: {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"I just finished meeting with {row['Name']} for their {visit_count_str} visit. As you know, they're a {row['Age']}-year-old {row['Gender']} "
        f"who lives at {row['Address']}. {row['Name']} has been dealing with {row['InitialCondition']} for some time now, which can't be easy. "
        f"On top of that, they're managing some long-term conditions: {row['LongTermConditions'].lower()}, as well as {row['SecondaryConditions'].lower()}. "
        f"It's also worth noting that {row['Name']} {allergies_str}, which we always need to keep in mind.\n\n"
        f"During today's {row['VisitType']} on {row['VisitDate']}, {row['Name']} shared that they've been experiencing {symptoms_str} "
        f"I could see they were a bit worried, so I made sure to take my time and do a thorough check-up. Their vitals were as follows: "
        f"blood pressure {row['BloodPressure']}, pulse {row['Pulse']} bpm, oxygen saturation at {row['SpO2']}, "
        f"body temperature {row['Temperature']}°C, weight {row['Weight']} kg, and height {row['Height']} cm. "
        f"After our discussion and examination, I believe we're looking at {row['Diagnosis'].lower()}. I explained this to {row['Name']} and made sure they understood what this means for them. "
        f"In terms of treatment, {row['Name']} {medication_str}. I made sure to explain how to take the medication properly and what side effects to watch out for. "
        f"We also got some lab work done, which showed {lab_results_str} As for procedures, {row['Name']} {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "didn't need any medications" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"was prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nI also made sure to follow up on {row['Name']}'s last visit on {previous_visit_date}. At that time, they were dealing with {previous_symptoms} "
            f"We had diagnosed it as {previous_diagnosis}, and {row['Name']} {previous_medication}. "
            f"The lab results from that visit showed {previous_lab_results} My notes from that visit mention: {previous_medical_notes}. "
            f"I made sure to discuss how things have changed since then and if {row['Name']} had any lingering concerns from that visit."
        )
    
    user_message += (
        f"\n\nOverall, I tried to address all of {row['Name']}'s concerns and make sure they left feeling heard and cared for. "
        f"I emphasized the importance of following the treatment plan and encouraged them to reach out if they have any questions or if their symptoms change."
    )
    
    return user_message.replace('..', '.').strip()

def problem_oriented_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "No known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"Allergies: {row['Allergies'].lower()}"
    medication_str = "No new medications prescribed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"Prescribed: {row['MedicationPrescribed'].lower()}"
    procedures_str = "No procedures performed" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"Procedures: {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Patient: {row['Name']} (ID: {row['PatientID']}) | {row['Age']}-year-old {row['Gender']} | Visit {visit_count_str} - {row['VisitType']} on {row['VisitDate']}\n\n"
        f"Problem List:\n"
        f"1. {row['InitialCondition']} (Primary)\n"
        f"2. {row['LongTermConditions'].lower()} (Chronic)\n"
        f"3. {row['SecondaryConditions'].lower()} (Secondary)\n"
        f"4. {allergies_str}\n"
        f"5. New issue: {row['Diagnosis'].lower()}\n\n"
        f"Subjective:\n"
        f"Patient reports {symptoms_str}\n\n"
        f"Objective:\n"
        f"- Vitals: BP {row['BloodPressure']}, HR {row['Pulse']} bpm, SpO2 {row['SpO2']}, Temp {row['Temperature']}°C\n"
        f"- Weight: {row['Weight']} kg, Height: {row['Height']} cm\n"
        f"- Labs: {lab_results_str}\n"
        f"- {procedures_str}\n\n"
        f"Assessment:\n"
        f"{row['Diagnosis'].lower()}\n\n"
        f"Plan:\n"
        f"1. {medication_str}\n"
        f"2. Follow-up on lab results\n"
        f"3. Monitor symptoms and adjust treatment as necessary"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "No medications prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"Prescribed: {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nPrevious Visit ({previous_visit_date}) Follow-up:\n"
            f"- Prior symptoms: {previous_symptoms}\n"
            f"- Prior diagnosis: {previous_diagnosis}\n"
            f"- Prior treatment: {previous_medication}\n"
            f"- Prior labs: {previous_lab_results}\n"
            f"- Progress notes: {previous_medical_notes}\n"
            f"- Current status: [Improved/Stable/Worsened] - Adjust treatment plan accordingly."
        )
    
    return user_message.replace('..', '.').strip()

def storytelling_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "doesn't have any allergies we need to worry about" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"is allergic to {row['Allergies'].lower()}, so we need to be careful about that"
    medication_str = "doesn't need any new meds" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"is going to start taking {row['MedicationPrescribed'].lower()}"
    procedures_str = "we didn't need to do any special procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we had to do {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"So, let me tell you about {row['Name']} who came in for their {visit_count_str} visit today. You know, the {row['Age']}-year-old {row['Gender']} "
        f"who lives over at {row['Address']}? Well, they've been dealing with {row['InitialCondition']} for a while now. "
        f"Poor thing's also got {row['LongTermConditions'].lower()} to manage long-term, and {row['SecondaryConditions'].lower()} on top of that. "
        f"Oh, and just so you know, {row['Name']} {allergies_str}.\n\n"
        f"Anyway, they came in for a {row['VisitType']} today, {row['VisitDate']}, and you wouldn't believe what they told me. "
        f"They've been feeling {symptoms_str} Can you imagine? So of course, I checked them over thoroughly. "
        f"Their blood pressure was {row['BloodPressure']}, heart racing at {row['Pulse']} beats per minute, "
        f"oxygen levels at {row['SpO2']}, and running a temp of {row['Temperature']}°C. "
        f"They're weighing in at {row['Weight']} kg and standing {row['Height']} cm tall these days.\n\n"
        f"After looking at everything, I reckon we're dealing with {row['Diagnosis'].lower()} here. "
        f"I told {row['Name']} not to worry too much, and that {medication_str}. "
        f"We ran some tests, and get this, the results showed {lab_results_str} Oh, and {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "they didn't need any medication" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we put them on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh, and remember when {row['Name']} was here last time, {previous_visit_date}? "
            f"They were complaining about {previous_symptoms} We thought it was {previous_diagnosis} back then, and {previous_medication}. "
            f"The lab work from that visit showed {previous_lab_results} I wrote down in my notes: {previous_medical_notes}. "
            f"Interesting to see how things have changed since then, isn't it?"
        )
    
    user_message += (
        f"\n\nAnyway, that's the scoop on {row['Name']}. I'll keep an eye on them and see how they progress. "
        f"Let's hope they start feeling better soon!"
    )
    
    return user_message.replace('..', '.').strip()

def casual_colleague_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no new meds" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"{row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Hey, got a sec? Just saw {row['Name']} - you know, patient ID {row['PatientID']}? It was their {visit_count_str} visit. "
        f"Quick rundown: {row['Age']}-year-old {row['Gender']}, lives at {row['Address']}. "
        f"Main issue is {row['InitialCondition']}, but they're also dealing with {row['LongTermConditions'].lower()} long-term, "
        f"and {row['SecondaryConditions'].lower()} on the side. {allergies_str.capitalize()}, by the way.\n\n"
        f"So, they came in today ({row['VisitDate']}) for a {row['VisitType']}. Said they were feeling {symptoms_str} "
        f"Vitals were: BP {row['BloodPressure']}, pulse {row['Pulse']}, O2 sat {row['SpO2']}, temp {row['Temperature']}°C. "
        f"They're at {row['Weight']} kg, {row['Height']} cm. "
        f"After checking them out, I'm thinking it's {row['Diagnosis'].lower()}. "
        f"Treatment plan: {medication_str}. "
        f"Lab results came back showing {lab_results_str} As for procedures, {procedures_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh, and about their last visit on {previous_visit_date} - they came in with {previous_symptoms} "
            f"We diagnosed it as {previous_diagnosis}, put them on {previous_medication}. "
            f"Labs showed {previous_lab_results} I noted: {previous_medical_notes}. "
            f"Seems like things have {['improved', 'changed', 'stayed about the same'][random.randint(0,2)]} since then."
        )
    
    user_message += (
        f"\n\nAnyway, that's the gist of it. Let me know if you need any more details!"
    )
    
    return user_message.replace('..', '.').strip()

def formal_consultation_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no new medications were prescribed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"the following medications were prescribed: {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures were performed" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"the following procedures were conducted: {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"I am writing to provide a comprehensive update on patient {row['Name']} (ID: {row['PatientID']}), whom I saw for their {visit_count_str} consultation. "
        f"The patient is a {row['Age']}-year-old {row['Gender']} residing at {row['Address']}. "
        f"As you are aware, the patient has a history of {row['InitialCondition']}. Additionally, they have been diagnosed with "
        f"the following chronic conditions: {row['LongTermConditions'].lower()}, as well as secondary conditions including {row['SecondaryConditions'].lower()}. "
        f"It is noteworthy that the patient has {allergies_str}.\n\n"
        f"During this {row['VisitType']} on {row['VisitDate']}, the patient presented with the following symptoms: {symptoms_str} "
        f"Upon examination, the patient's vital signs were as follows: blood pressure {row['BloodPressure']}, pulse {row['Pulse']} bpm, oxygen saturation (SpO2) at {row['SpO2']}, "
        f"body temperature {row['Temperature']}°C, weight {row['Weight']} kg, and height {row['Height']} cm. "
        f"After a thorough evaluation, I have determined that the patient is suffering from {row['Diagnosis'].lower()}. "
        f"In light of this diagnosis, {medication_str}. "
        f"Laboratory investigations revealed the following: {lab_results_str} Furthermore, {procedures_str}"
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications were prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"the following medications were prescribed: {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nFor context, I would like to refer to the patient's previous consultation on {previous_visit_date}. At that time, the patient reported {previous_symptoms} "
            f"The diagnosis was {previous_diagnosis}, and {previous_medication}. "
            f"Laboratory results from that visit indicated {previous_lab_results} My clinical notes from that consultation state: {previous_medical_notes}. "
            f"This information has been taken into account when formulating the current treatment plan."
        )
    
    user_message += (
        f"\n\nMoving forward, I recommend close monitoring of the patient's condition and adherence to the prescribed treatment regimen. "
        f"Should you have any questions or require further clarification, please do not hesitate to contact me."
    )
    
    return user_message.replace('..', '.').strip()

def casual_dictation_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies to worry about" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "doesn't need any new meds" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I've put them on {row['MedicationPrescribed'].lower()}"
    procedures_str = "we didn't do any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we did {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Alright, let's get this note down for {row['Name']}. Patient ID is {row['PatientID']}, and this was their {visit_count_str} time here. "
        f"We're looking at a {row['Age']}-year-old {row['Gender']}, address is {row['Address']}. "
        f"Main thing they're dealing with is {row['InitialCondition']}. Oh, and they've got some long-term stuff going on too: {row['LongTermConditions'].lower()}. "
        f"Can't forget about these other issues: {row['SecondaryConditions'].lower()}. And just to note, {allergies_str}.\n\n"
        f"So, they came in today, {row['VisitDate']}, for a {row['VisitType']}. Their main complaints were {symptoms_str} "
        f"Vitals were... let's see... BP was {row['BloodPressure']}, pulse {row['Pulse']}, O2 sat {row['SpO2']}, "
        f"temp {row['Temperature']}°C. They're weighing in at {row['Weight']} kg and standing {row['Height']} cm tall. "
        f"After checking them out, I'm thinking we're dealing with {row['Diagnosis'].lower()} here. "
        f"As for treatment, {medication_str}. "
        f"Lab work came back showing {lab_results_str} Oh, and {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "they didn't need any meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we put them on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh yeah, almost forgot. They were here before on {previous_visit_date}. Back then, they were complaining about {previous_symptoms} "
            f"We thought it was {previous_diagnosis}, and {previous_medication}. "
            f"Labs from that time showed {previous_lab_results} I had jotted down: {previous_medical_notes}. "
            f"Looks like things have {['gotten better', 'changed a bit', 'stayed pretty much the same'][random.randint(0,2)]} since then."
        )
    
    user_message += (
        f"\n\nI think that covers it. We'll keep an eye on how they're doing and adjust as needed. End of note."
    )
    
    return user_message.replace('..', '.').strip()

def reflective_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "I didn't prescribe any new medications" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "I didn't perform any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"I performed {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"I've just finished seeing {row['Name']} (Patient ID: {row['PatientID']}) for their {visit_count_str} visit, and I wanted to take a moment to reflect on the consultation. "
        f"{row['Name']} is a {row['Age']}-year-old {row['Gender']} who lives at {row['Address']}. "
        f"What struck me during our interaction was how they've been managing their {row['InitialCondition']}. "
        f"It's not easy dealing with that, especially considering their other long-term conditions: {row['LongTermConditions'].lower()}. "
        f"And let's not forget the additional challenges posed by {row['SecondaryConditions'].lower()}. "
        f"I made sure to keep in mind that they have {allergies_str}.\n\n"
        f"Today's visit ({row['VisitDate']}) was a {row['VisitType']}. {row['Name']} came in describing {symptoms_str} "
        f"I found myself particularly concerned about these symptoms, given their medical history. "
        f"The vital signs told an interesting story: BP {row['BloodPressure']}, pulse {row['Pulse']} bpm, SpO2 {row['SpO2']}, "
        f"temperature {row['Temperature']}°C, weight {row['Weight']} kg, and height {row['Height']} cm. "
        f"After careful consideration, I concluded we're dealing with {row['Diagnosis'].lower()}. "
        f"In terms of treatment, {medication_str}. I hope this approach will provide some relief. "
        f"The lab results revealed {lab_results_str} These findings certainly add another layer to consider. As for procedures, {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "I didn't prescribe any medications" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nReflecting on {row['Name']}'s previous visit on {previous_visit_date}, I recall they were experiencing {previous_symptoms} "
            f"At that time, I diagnosed it as {previous_diagnosis}, and {previous_medication}. "
            f"The lab work then showed {previous_lab_results} I had noted: {previous_medical_notes}. "
            f"Comparing that visit to today's, I can see {['some improvement', 'some changes', 'that the situation has remained relatively stable'][random.randint(0,2)]}. "
            f"This progression (or lack thereof) has certainly influenced my current assessment and treatment plan."
        )
    
    user_message += (
        f"\n\nAs I conclude this reflection, I'm reminded of the complexity of medical care. "
        f"Each patient, like {row['Name']}, brings a unique set of circumstances that require careful consideration. "
        f"I'll continue to monitor their progress closely and adjust our approach as needed. "
        f"It's cases like these that remind me why I became a doctor in the first place."
    )
    
    return user_message.replace('..', '.').strip()

def narrative_assessment_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "no new medications were necessary" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures were required" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we performed {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"{row['Name']}, a {row['Age']}-year-old {row['Gender']}, came in for their {visit_count_str} visit today. As they settled into the exam room, "
        f"I couldn't help but reflect on their journey with {row['InitialCondition']}. It's been a complex case, further complicated by "
        f"their long-term conditions of {row['LongTermConditions'].lower()} and the more recent developments of {row['SecondaryConditions'].lower()}. "
        f"Keeping their {allergies_str} in mind, I began our consultation.\n\n"
        f"Today's {row['VisitType']} on {row['VisitDate']} revealed new challenges. {row['Name']} described {symptoms_str} "
        f"Their voice carried a hint of worry, understandable given their history. As I conducted the examination, the numbers told their own story: "
        f"blood pressure at {row['BloodPressure']}, a pulse of {row['Pulse']} bpm, oxygen saturation holding at {row['SpO2']}, "
        f"and a temperature of {row['Temperature']}°C. At {row['Weight']} kg and {row['Height']} cm, their physical presence in the room seemed to reflect their medical journey.\n\n"
        f"Piecing together the symptoms, history, and examination findings, I arrived at a diagnosis of {row['Diagnosis'].lower()}. "
        f"This conclusion led me to adjust our approach: {medication_str}. I explained each decision, watching for understanding in their eyes. "
        f"The lab results added another layer to our discussion, showing {lab_results_str} These findings guided our next steps. {procedures_str.capitalize()}, "
        f"each action carefully chosen to address {row['Name']}'s unique situation."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications were prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{previous_visit_info['MedicationPrescribed'].lower()} was prescribed"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nAs we talked, I couldn't help but recall {row['Name']}'s last visit on {previous_visit_date}. The echoes of that day – {previous_symptoms} – "
            f"still resonated. We had navigated the waters of {previous_diagnosis} then, and {previous_medication}. "
            f"The lab work had revealed {previous_lab_results}, a piece of the puzzle that influenced today's decisions. "
            f"My notes from that day – {previous_medical_notes} – served as a bridge between then and now, highlighting the evolving nature of {row['Name']}'s health journey."
        )
    
    user_message += (
        f"\n\nAs {row['Name']} left the office, I felt the weight of our shared medical narrative. Each visit adds a chapter to their story, "
        f"and I'm committed to guiding them through each twist and turn. We'll continue to monitor, adjust, and hope for positive developments in the pages to come."
    )
    
    return user_message.replace('..', '.').strip()

def holistic_care_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "we decided against introducing new medications" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we initiated {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures were deemed necessary" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we carried out {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"In our ongoing care for {row['Name']}, a {row['Age']}-year-old {row['Gender']} residing at {row['Address']}, we had our {visit_count_str} consultation today. "
        f"As always, I approached this visit with a holistic mindset, considering not just the immediate concerns but the full tapestry of {row['Name']}'s health. "
        f"Their journey with {row['InitialCondition']} continues to be central, interwoven with the challenges posed by {row['LongTermConditions'].lower()} "
        f"and the more recent developments of {row['SecondaryConditions'].lower()}. The additional consideration of {allergies_str} adds another layer to their care.\n\n"
        f"Today's {row['VisitType']} on {row['VisitDate']} brought new threads to this complex weave. {row['Name']} presented with {symptoms_str} "
        f"These symptoms, while concerning, offer us insights into the broader picture of their health. The vital signs we recorded – "
        f"blood pressure of {row['BloodPressure']}, pulse at {row['Pulse']} bpm, oxygen saturation of {row['SpO2']}, and a temperature of {row['Temperature']}°C – "
        f"along with their current weight of {row['Weight']} kg and height of {row['Height']} cm, all contribute to our understanding of their physical state.\n\n"
        f"After careful consideration of all factors, I've determined we're dealing with {row['Diagnosis'].lower()}. This diagnosis isn't just a label, "
        f"but a starting point for our adjusted care plan. In light of this, {medication_str}. Each decision is made with the aim of supporting {row['Name']}'s overall well-being. "
        f"The laboratory results, showing {lab_results_str}, have been instrumental in shaping our approach. In terms of procedures, {procedures_str}, "
        f"always keeping in mind the broader context of {row['Name']}'s health landscape."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no medications were prescribed" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{previous_visit_info['MedicationPrescribed'].lower()} was prescribed"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nReflecting on our last encounter on {previous_visit_date}, I'm reminded of the continuity of care. At that time, {row['Name']} was experiencing {previous_symptoms} "
            f"We had identified {previous_diagnosis} and {previous_medication}. The laboratory investigations had shown {previous_lab_results} "
            f"My notes from that visit – {previous_medical_notes} – serve as a valuable reference point, allowing us to track the evolution of {row['Name']}'s health status and adjust our care accordingly."
        )
    
    user_message += (
        f"\n\nAs we move forward, our focus remains on providing comprehensive, patient-centered care for {row['Name']}. "
        f"We'll continue to monitor their progress, adapt our strategies as needed, and work together towards the best possible health outcomes. "
        f"This ongoing journey reminds us of the importance of seeing the whole person, not just the sum of their medical conditions."
    )
    
    return user_message.replace('..', '.').strip()

def patient_journey_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "we didn't need to start any new medications" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we started {row['MedicationPrescribed'].lower()}"
    procedures_str = "we didn't need to do any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we performed {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Today marks another milestone in {row['Name']}'s health journey – their {visit_count_str} visit with us. At {row['Age']} years old, "
        f"this {row['Gender']} patient from {row['Address']} continues to navigate the complexities of their health with remarkable resilience. "
        f"Their primary battle with {row['InitialCondition']} has been a significant chapter in their story, further enriched by the ongoing narrative of "
        f"{row['LongTermConditions'].lower()} and the more recent plot twists of {row['SecondaryConditions'].lower()}. "
        f"The subplot of {allergies_str} adds another layer to their unique health chronicle.\n\n"
        f"This {row['VisitType']} on {row['VisitDate']} unveiled new developments in {row['Name']}'s saga. They arrived describing {symptoms_str} "
        f"These symptoms, like breadcrumbs, led us through the forest of diagnostic possibilities. The vital signs we recorded – "
        f"a blood pressure of {row['BloodPressure']}, heart rate of {row['Pulse']} bpm, oxygen levels at {row['SpO2']}, and a temperature of {row['Temperature']}°C – "
        f"along with their current weight of {row['Weight']} kg and height of {row['Height']} cm, all contributed to the unfolding story.\n\n"
        f"After carefully piecing together the clues, we've reached a new understanding: {row['Diagnosis'].lower()}. This diagnosis isn't the end of a chapter, "
        f"but rather the beginning of a new one in {row['Name']}'s ongoing health narrative. In response to this plot development, {medication_str}. "
        f"Our laboratory investigations added depth to the story, revealing {lab_results_str} These findings will guide our path forward. "
        f"As for medical interventions, {procedures_str}, each step carefully considered in the context of {row['Name']}'s broader health story."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "we didn't prescribe any new medications" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we prescribed {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nReflecting on the previous chapter of {row['Name']}'s journey, their visit on {previous_visit_date}, provides valuable context. "
            f"Then, they were grappling with {previous_symptoms} We had identified the challenge as {previous_diagnosis}, and in response, {previous_medication}. "
            f"The lab work had revealed {previous_lab_results}, pieces of the puzzle that have influenced our current understanding. "
            f"My notes from that day – {previous_medical_notes} – serve as a bridge between then and now, highlighting the evolution of {row['Name']}'s health narrative."
        )
    
    user_message += (
        f"\n\nAs we close this latest chapter in {row['Name']}'s health journey, we look ahead with cautious optimism. "
        f"Their story is far from over, and we'll continue to be there, helping to navigate each twist and turn. "
        f"We'll vigilantly monitor their progress, ready to adapt our approach as new chapters unfold. "
        f"Through it all, we remain committed to ensuring that {row['Name']}'s health story is one of perseverance, improvement, and hope."
    )
    
    return user_message.replace('..', '.').strip()

def thoughtful_reflection_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "I didn't prescribe any new medications" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "I didn't perform any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"I performed {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"I've just finished seeing {row['Name']} for their {visit_count_str} visit, and I can't help but pause to reflect on their case. "
        f"There's something about {row['Name']} - a {row['Age']}-year-old {row['Gender']} from {row['Address']} - that really makes me think about the complexities of medicine. "
        f"They've been battling {row['InitialCondition']} for so long, and now with {row['LongTermConditions'].lower()} and {row['SecondaryConditions'].lower()} in the mix, "
        f"it's like watching someone juggle while walking a tightrope. And let's not forget about their {allergies_str} - another ball in the air.\n\n"
        f"Today's {row['VisitType']} ({row['VisitDate']}) was particularly interesting. When {row['Name']} mentioned {symptoms_str}, I found myself really tuning in. "
        f"You know that feeling when a patient says something and your mind starts racing through possibilities? That was me today. "
        f"As I checked their vitals - BP {row['BloodPressure']}, pulse {row['Pulse']}, O2 sat {row['SpO2']}, temp {row['Temperature']}°C - I was piecing together this puzzle. "
        f"At {row['Weight']} kg and {row['Height']} cm, {row['Name']} seemed {['frailer', 'stronger', 'about the same'][random.randint(0,2)]} than last time, which got me thinking...\n\n"
        f"After our chat and exam, I'm leaning towards {row['Diagnosis'].lower()}. It fits, but there's always that nagging voice in the back of my mind questioning if I've missed something. "
        f"Anyway, {medication_str}. I hope it helps, but only time will tell. The lab results showing {lab_results_str} add another layer to consider. "
        f"As for procedures, {procedures_str}. Sometimes I wonder if we're doing too much or too little - it's a fine line to walk."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "I didn't prescribe anything" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I put them on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nThinking back to {row['Name']}'s last visit on {previous_visit_date}, I remember they came in with {previous_symptoms} "
            f"We thought it was {previous_diagnosis} then, and {previous_medication}. The labs showed {previous_lab_results} "
            f"I wrote in my notes: '{previous_medical_notes}.' It's fascinating to see how things have evolved. "
            f"Sometimes I wonder if I made the right call back then. Hindsight is 20/20, they say, but in medicine, it's often more like a foggy mirror."
        )
    
    user_message += (
        f"\n\nAs I wrap up my notes on {row['Name']}, I'm struck by how each patient teaches me something new. "
        f"This case reminds me why I got into medicine - the challenge, the mystery, the human element. "
        f"I'll keep a close eye on {row['Name']}'s progress, but for now, I'm left pondering the beautiful complexity of the human body and the art of healing. "
        f"Days like today make me grateful for this profession, challenges and all."
    )
    
    return user_message.replace('..', '.').strip()

def stream_of_consciousness_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergic to {row['Allergies'].lower()}"
    medication_str = "no new meds" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"started on {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"did {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Okay, just saw {row['Name']}... {visit_count_str} visit... let's see, {row['Age']} years old, {row['Gender']}, lives at {row['Address']}... "
        f"right, the one with {row['InitialCondition']}. Gosh, they've been through a lot. Also dealing with {row['LongTermConditions'].lower()} "
        f"and now {row['SecondaryConditions'].lower()}. Oh, and {allergies_str}, can't forget that. Where was I? Right, today's visit.\n\n"
        f"So, {row['VisitType']} today, {row['VisitDate']}. They came in saying {symptoms_str} Hm, interesting. Vitals were... hang on, "
        f"let me find my scribbles... ah, BP {row['BloodPressure']}, pulse {row['Pulse']}, oxygen {row['SpO2']}, temp {row['Temperature']}°C. "
        f"Weight {row['Weight']} kg, height {row['Height']} cm. Does that seem right? Yeah, I think so.\n\n"
        f"Okay, so after talking and examining, I'm thinking it's {row['Diagnosis'].lower()}. Yeah, that fits. So what did I do... right, {medication_str}. "
        f"Hope that helps. Oh, labs. Almost forgot about those. They showed {lab_results_str} Need to think about what that means. "
        f"And procedures... {procedures_str}. Did I miss anything? Don't think so."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh wait, they were here before, weren't they? When was it... {previous_visit_date}, that's right. "
            f"They had {previous_symptoms} We thought {previous_diagnosis}, gave them {previous_medication}. Labs were {previous_lab_results} "
            f"I wrote something like... oh yeah, '{previous_medical_notes}.' Huh, interesting to see how things have changed. Or have they? Need to think about that."
        )
    
    user_message += (
        f"\n\nAnyway, I think that's everything on {row['Name']} for now. Need to keep an eye on them, see how they do. "
        f"Maybe adjust things next time? We'll see. Okay, who's next? My coffee's probably cold by now..."
    )
    
    return user_message.replace('..', '.').strip()

def empathetic_narrative_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no known allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "we decided against new medications for now" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "we didn't need to perform any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we performed {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"I just finished seeing {row['Name']} for their {visit_count_str} visit, and I have to say, their resilience never ceases to amaze me. "
        f"At {row['Age']} years old, this {row['Gender']} patient from {row['Address']} has been through so much with their {row['InitialCondition']}. "
        f"Add to that the daily challenges of {row['LongTermConditions'].lower()} and the recent complications of {row['SecondaryConditions'].lower()}, "
        f"and you've got someone who's fighting battles on multiple fronts. Oh, and we always need to keep in mind their {allergies_str}.\n\n"
        f"Today's {row['VisitType']} ({row['VisitDate']}) was particularly touching. When {row['Name']} told me about {symptoms_str}, I could see the worry in their eyes. "
        f"It's moments like these that remind me why I became a doctor. As I took their vitals - BP {row['BloodPressure']}, pulse {row['Pulse']}, "
        f"oxygen levels at {row['SpO2']}, temperature {row['Temperature']}°C - I tried to reassure them. At {row['Weight']} kg and {row['Height']} cm, "
        f"they seemed {['a bit frailer', 'somehow stronger', 'much the same'][random.randint(0,2)]} than last time, which tugged at my heart.\n\n"
        f"After our discussion and examination, I believe we're dealing with {row['Diagnosis'].lower()}. Explaining this to {row['Name']}, I could see a mix of relief and concern on their face. "
        f"We talked through the treatment plan, and {medication_str}. I made sure to explain everything clearly and answer all their questions. "
        f"The lab results showing {lab_results_str} added another piece to the puzzle. As for procedures, {procedures_str}. "
        f"Throughout it all, I was struck by {row['Name']}'s courage and willingness to face whatever comes their way."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "we didn't need to prescribe any new medications" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we started them on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nReflecting on {row['Name']}'s last visit on {previous_visit_date}, I remember how worried they were about {previous_symptoms} "
            f"We had diagnosed it as {previous_diagnosis}, and {previous_medication}. The labs had shown {previous_lab_results} "
            f"I had noted: '{previous_medical_notes}.' Seeing how things have progressed since then, I'm reminded of the ongoing nature of healthcare "
            f"and the importance of being there for our patients through all the ups and downs."
        )
    
    user_message += (
        f"\n\nAs {row['Name']} left the office today, I couldn't help but feel a mix of concern and hope. Their journey is far from over, "
        f"but I'm committed to being there every step of the way. We'll keep monitoring their progress closely and adjust our approach as needed. "
        f"It's patients like {row['Name']} who remind me of the profound privilege and responsibility we have as healthcare providers. "
        f"Their trust in us is a precious thing, and I'm determined to do everything I can to help them through this challenging time."
    )
    
    return user_message.replace('..', '.').strip()

def casual_narrative_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies to worry about" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "doesn't need any new meds" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"started on {row['MedicationPrescribed'].lower()}"
    procedures_str = "didn't need any procedures" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"had {row['Procedures'].lower()} done"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Alright, so {row['Name']} came in for their {visit_count_str} visit today. They're {row['Age']}, {row['Gender']}, living over at {row['Address']}. "
        f"Poor thing's been dealing with {row['InitialCondition']} for a while now. On top of that, they've got {row['LongTermConditions'].lower()} "
        f"and now {row['SecondaryConditions'].lower()} to manage. Oh, and they've got {allergies_str}.\n\n"
        f"So, today's visit ({row['VisitDate']}) was a {row['VisitType']}. {row['Name']} came in saying they felt {symptoms_str} "
        f"Checked them over, vitals were BP {row['BloodPressure']}, pulse running at {row['Pulse']}, oxygen at {row['SpO2']}, "
        f"and temp was {row['Temperature']}°C. They're weighing in at {row['Weight']} kg and standing {row['Height']} cm tall.\n\n"
        f"After chatting and looking them over, looks like we're dealing with {row['Diagnosis'].lower()}. {medication_str}. "
        f"Ran some tests, and the results show {lab_results_str} As for procedures, {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "didn't need any meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"was put on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh yeah, almost forgot. Last time {row['Name']} was here ({previous_visit_date}), they were dealing with {previous_symptoms} "
            f"We thought it was {previous_diagnosis} back then, and {previous_medication}. Labs showed {previous_lab_results} "
            f"I jotted down: '{previous_medical_notes}.' Interesting to see how things have changed since then."
        )
    
    user_message += (
        f"\n\nAnyway, that's the scoop on {row['Name']} for now. We'll keep an eye on how they're doing and see them again if needed. "
        f"Fingers crossed they start feeling better soon!"
    )
    
    return user_message.replace('..', '.').strip()

def relaxed_summary_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergic to {row['Allergies'].lower()}"
    medication_str = "no new meds needed" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"prescribed {row['MedicationPrescribed'].lower()}"
    procedures_str = "no procedures needed" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"{row['Procedures'].lower()} was done"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Just saw {row['Name']} for visit number {visit_count_str}. Quick rundown: {row['Age']} years old, {row['Gender']}, lives at {row['Address']}. "
        f"Main issue is still {row['InitialCondition']}, but they're also juggling {row['LongTermConditions'].lower()} long-term "
        f"and {row['SecondaryConditions'].lower()} on the side. {allergies_str.capitalize()}, by the way.\n\n"
        f"Came in today ({row['VisitDate']}) for a {row['VisitType']}. Said they were feeling {symptoms_str} "
        f"Vitals were pretty standard: BP {row['BloodPressure']}, pulse {row['Pulse']}, oxygen {row['SpO2']}, temp {row['Temperature']}°C. "
        f"They're at {row['Weight']} kg, {row['Height']} cm. After checking them out, I'm thinking it's {row['Diagnosis'].lower()}. "
        f"Treatment-wise, {medication_str}. Lab results came back showing {lab_results_str} Oh, and {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "no meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"{previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nLooking back at their last visit ({previous_visit_date}), they came in with {previous_symptoms} "
            f"We thought {previous_diagnosis}, gave them {previous_medication}. Labs were {previous_lab_results} "
            f"I wrote down: '{previous_medical_notes}.' Seems like things have {['improved a bit', 'changed somewhat', 'stayed about the same'][random.randint(0,2)]} since then."
        )
    
    user_message += (
        f"\n\nThat's about it for {row['Name']}. We'll keep tabs on them, see how they do. Hopefully, they'll be feeling better next time around."
    )
    
    return user_message.replace('..', '.').strip()

def conversational_recap_prompt(row, previous_visit_info):
    visit_count_str = {1: "first", 2: "second", 3: "third"}.get(row['VisitCount'], f"{row['VisitCount']}th")
    
    allergies_str = "no allergies to speak of" if row['Allergies'].strip().lower() in ['none reported', 'none'] else f"allergies to {row['Allergies'].lower()}"
    medication_str = "we're holding off on new meds for now" if row['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"I've put them on {row['MedicationPrescribed'].lower()}"
    procedures_str = "we skipped any procedures this time" if row['Procedures'].strip().lower() in ['none', 'none performed', 'none at this time'] else f"we did {row['Procedures'].lower()}"

    symptoms_str = row['Symptoms'].rstrip('.').lower() + "."
    lab_results_str = row['LabResults'].rstrip('.').lower() + "."
    procedures_str = procedures_str.rstrip('.').lower() + "."
    
    user_message = (
        f"Hey, just wrapped up with {row['Name']}. It was their {visit_count_str} time here. You know, the {row['Age']}-year-old {row['Gender']} "
        f"from {row['Address']}? Yeah, the one dealing with {row['InitialCondition']}. Remember they've also got {row['LongTermConditions'].lower()} "
        f"going on, and now {row['SecondaryConditions'].lower()} to boot. Oh, and {allergies_str} – can't forget that.\n\n"
        f"So, they popped in today ({row['VisitDate']}) for a {row['VisitType']}. Main complaints were {symptoms_str} "
        f"Vitals were... let's see... BP was {row['BloodPressure']}, heart rate {row['Pulse']}, oxygen levels at {row['SpO2']}, "
        f"and running a temp of {row['Temperature']}°C. They're tipping the scales at {row['Weight']} kg and standing {row['Height']} cm tall.\n\n"
        f"After chatting and looking them over, I'm thinking we're dealing with {row['Diagnosis'].lower()} here. "
        f"As for treatment, {medication_str}. The lab work came back showing {lab_results_str} And {procedures_str}."
    )
    
    if previous_visit_info is not None and not previous_visit_info.empty:
        previous_visit_date = previous_visit_info['VisitDate']
        previous_symptoms = previous_visit_info['Symptoms'].rstrip('.').lower() + "."
        previous_diagnosis = previous_visit_info['Diagnosis'].lower()
        previous_medication = "they didn't need any meds" if previous_visit_info['MedicationPrescribed'].strip().lower() in ['none prescribed', 'none', 'none at this time'] else f"we put them on {previous_visit_info['MedicationPrescribed'].lower()}"
        previous_lab_results = previous_visit_info['LabResults'].rstrip('.').lower() + "."
        previous_medical_notes = previous_visit_info['MedicalNotes'].rstrip('.')
        
        user_message += (
            f"\n\nOh, right – last time they were here ({previous_visit_date}), they were dealing with {previous_symptoms} "
            f"We figured it was {previous_diagnosis} back then, and {previous_medication}. Labs showed {previous_lab_results} "
            f"I had scribbled down: '{previous_medical_notes}.' Kind of interesting to see how things have shifted since then."
        )
    
    user_message += (
        f"\n\nAnyway, that's the lowdown on {row['Name']}. We'll keep an eye on how they're doing. "
        f"Here's hoping they start feeling more like themselves soon. If not, well, I guess we'll be seeing them again before too long."
    )
    
    return user_message.replace('..', '.').strip()



# List of all prompt styles
PROMPT_STYLES = [
    current_prompt,
    narrative_prompt,
    conversational_prompt,
    detailed_clinical_prompt,
    empathetic_prompt,
    problem_oriented_prompt,
    storytelling_prompt,
    casual_colleague_prompt,
    formal_consultation_prompt,
    casual_dictation_prompt,
    reflective_prompt,
    narrative_assessment_prompt,
    holistic_care_prompt,
    patient_journey_prompt,
    thoughtful_reflection_prompt,
    stream_of_consciousness_prompt,
    empathetic_narrative_prompt,
    casual_narrative_prompt,
    relaxed_summary_prompt,
    conversational_recap_prompt
]

# Queue to keep track of recently used styles
recent_styles = deque(maxlen=5)

def choose_prompt_style():
    available_styles = [style for style in PROMPT_STYLES if style not in recent_styles]
    if not available_styles:
        available_styles = PROMPT_STYLES  # If all styles have been used recently, reset
    
    chosen_style = random.choice(available_styles)
    recent_styles.append(chosen_style)
    return chosen_style

def create_natural_language_prompt(row, previous_visit_info):
    chosen_style = choose_prompt_style()
    user_message = chosen_style(row, previous_visit_info)
    
    return {
        "role": "user",
        "content": user_message
    }

