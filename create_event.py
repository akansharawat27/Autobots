import datefinder
from apiclient.discovery import build
from datetime import timedelta


def create_event(start_time_str, summary, list_email, credentials, duration=1, description=None, location=None):

    service = build("calendar", "v3", credentials=credentials)

    result = service.calendarList().list().execute()

    matches = list(datefinder.find_dates(start_time_str))
    if len(matches):
        start_time = matches[0]
        end_time = start_time + timedelta(hours=float(duration))

    attendees = [{'email': email} for email in list_email]

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'attendees': attendees
    }
    return service.events().insert(calendarId='primary', body=event).execute()


# create_event("2023-04-08 16:30", "Meeting", ["akansharawat.ind@gmail.com", "harshitsaini7777@gmail.com"])