import spacy
import re
from date_extract import convert_date_parameter
from dateutil.parser import parse, ParserError

# Load the spaCy NLP model
nlp = spacy.load('en_core_web_sm')

# Define regular expression pattern for email addresses
email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'


# Define function to extract attendees list from user prompt
def extract_attendees_list_from_user_prompt(user_prompt):
    # Process the user prompt with spaCy
    doc = nlp(user_prompt)

    # Extract values using spaCy's named entity recognition (NER)
    meeting_attendees = []

    for token in doc:
        if token.ent_type_ == 'PERSON':
            meeting_attendees.append(token.text)

    # Extract email addresses from the text using regular expression
    extracted_emails = re.findall(email_pattern, user_prompt)
    meeting_attendees.extend(extracted_emails)

    # Remove duplicates from the attendee list
    meeting_attendees = list(set(meeting_attendees))

    return meeting_attendees


def extract_meeting_time_from_user_prompt(user_prompt):
    # Process the user prompt with spaCy
    doc = nlp(user_prompt)
    meeting_time = None

    # Extract time value from user prompt
    time_regex = r'(?i)(\d{1,2}(\s?:\s?\d{1,2})?\s?[apm.]+)'
    time_match = re.search(time_regex, user_prompt)
    if time_match:
        meeting_time = time_match.group(1)
        # Convert time value to HH:MM:SS format
        meeting_time = parse(meeting_time).strftime("%H:%M:%S")

    # print('meeting_time_test', meeting_time)
    return meeting_time;


def extract_meeting_date_from_user_prompt(user_prompt):
    # Process the user prompt with spaCy
    doc = nlp(user_prompt)

    for token in doc:
        if token.ent_type_ == 'DATE':
            meeting_date = token.text

    if meeting_date is not None:
        meeting_date = convert_date_parameter(str(meeting_date))

    return meeting_date


# Define function to extract values from user prompt
def extract_values_from_user_prompt(user_prompt):
    # Process the user prompt with spaCy
    doc = nlp(user_prompt)

    # Extract values using spaCy's named entity recognition (NER)
    meeting_title = None
    meeting_date = None
    meeting_time = None
    meeting_attendees = []
    meeting_location = None

    for token in doc:
        if token.ent_type_ == 'DATE':
            meeting_date = token.text
        elif token.ent_type_ == 'PERSON':
            meeting_attendees.append(token.text)
        elif token.ent_type_ == 'GPE':
            meeting_location = token.text

    # Extract email addresses from the text using regular expression
    extracted_emails = re.findall(email_pattern, user_prompt)
    meeting_attendees.extend(extracted_emails)

    # Remove duplicates from the attendee list
    meeting_attendees = list(set(meeting_attendees))

    meeting_title = f"Meeting with {meeting_attendees}"

    # Extract time using dateutil
    meeting_time = parse(user_prompt, fuzzy=True).strftime("%H:%M:%S")

    if meeting_date is not None:
        meeting_date = convert_date_parameter(str(meeting_date))

    return meeting_title, meeting_date, meeting_time, meeting_attendees, meeting_location



# schedule a meeting with akansharawat.ind@gmail.com tomorrow at 4pm