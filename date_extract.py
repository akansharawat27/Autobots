import spacy
from datetime import datetime, timedelta
from spacy.matcher import Matcher
from dateutil.parser import parse
import re

# Load the 'en_core_web_sm' model
nlp = spacy.load('en_core_web_sm')

# Define a function to convert date parameters to "year-month-day" format
def convert_date_parameter(text):
    # Parse the input text with spaCy
    doc = nlp(text)

    # Define a spaCy Matcher pattern for date and time entities
    pattern = [
        {"ENT_TYPE": {"IN": ["DATE", "TIME"]}},
        {"LOWER": "at", "OP": "?"},
        {"ENT_TYPE": {"IN": ["TIME", "DATE"]}, "OP": "*"}
    ]

    # Initialize the Matcher
    matcher = Matcher(nlp.vocab)
    matcher.add('DATE_TIME', [pattern])

    # Initialize variables to store extracted date and time
    extracted_date = None
    extracted_time = None

    # Iterate through the matches in the parsed document
    for match_id, start, end in matcher(doc):
        # Extract the matched span
        span = doc[start:end]

        # Check if the span has an entity of type "DATE"
        if span.ents and span.ents[0].label_ == "DATE":
            # Set the extracted date as the entity text
            extracted_date = span.ents[0].text

        # Check if the span has an entity of type "TIME"
        elif span.ents and span.ents[0].label_ == "TIME":
            # Set the extracted time as the entity text
            extracted_time = span.ents[0].text

    # If no date is found, return None
    if extracted_date is None:
        return None

    # If no time is found, return the date in "year-month-day" format
    if extracted_time is None:
        # Handle special cases like "today", "tomorrow", "yesterday", "next week", "next month", "2 weeks later", "2 months later" separately
        if extracted_date in ['today', 'tomorrow', 'yesterday']:
            if extracted_date == 'today':
                extracted_date = datetime.now().date()
            elif extracted_date == 'tomorrow':
                extracted_date = datetime.now().date() + timedelta(days=1)
            elif extracted_date == 'yesterday':
                extracted_date = datetime.now().date() - timedelta(days=1)
            return extracted_date.strftime("%Y-%m-%d")
        elif extracted_date == 'next week':
            extracted_date = datetime.now().date() + timedelta(weeks=1)
            return extracted_date.strftime("%Y-%m-%d")
        elif extracted_date == 'next month':
            extracted_date = datetime.now().date() + timedelta(days=30)
            return extracted_date.strftime("%Y-%m-%d")
        elif re.match(r'\d+ weeks? later', extracted_date):
            weeks = int(re.findall(r'\d+', extracted_date)[0])
            extracted_date = datetime.now().date() + timedelta(weeks=weeks)
            return extracted_date.strftime("%Y-%m-%d")
        elif re.match(r'\d+ months? later', extracted_date):
            months = int(re.findall(r'\d+', extracted_date)[0])
            extracted_date = datetime.now().date() + timedelta(days=30 * months)
            return extracted_date.strftime("%Y-%m-%d")

    # If both date and time are found, return them in "year-month-day" format
    return f'{extracted_date}'
