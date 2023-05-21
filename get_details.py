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
    if not meeting_time:
        time_regex = r'(?i)(\d{1,2})[:\s]?(\d{0,2})?\s?([apAP][mM])'
        time_match = re.search(time_regex, user_prompt)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) if time_match.group(2) else "00"
            am_pm = time_match.group(3).lower()
            if am_pm == "pm" and int(hour) < 12:
                hour = str(int(hour) + 12)
            elif am_pm == "am" and hour == "12":
                hour = "00"
            meeting_time = f"{hour}:{minute}:00"
        else:
            meeting_time = None

    # print('meeting_time_test', meeting_time)
    return meeting_time;


def extract_meeting_date_from_user_prompt(user_prompt):
    # Process the user prompt with spaCy
    doc = nlp(user_prompt)
    meeting_date = None

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