import datetime
from googleapiclient.discovery import build
import pytz


# Function to get the free slots for a given date
def get_busy_slots(calendar_id, date, creds):

    # Specify the time zone for your calendar
    calendar_timezone = 'Asia/Kolkata'

    # Get the timezone object
    timezone_obj = pytz.timezone(calendar_timezone)

    # Get the current time in the specified timezone
    now = datetime.datetime.now(timezone_obj)

    # Get the timezone offset in hours and minutes
    offset = now.strftime("%z")
    offset_hours = int(offset[:3])
    offset_minutes = int(offset[3:])

    # Determine if the offset is positive or negative
    offset_sign = "-" if offset_hours < 0 else "+"
    offset_hours = abs(offset_hours)

    # Format the timezone offset as hours and minutes
    offset_formatted = "{:s}{:02d}:{:02d}".format(offset_sign, offset_hours, offset_minutes)

    # Create a service instance for the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    freebusy_query = {
        "timeMin": date + 'T' + str(datetime.time.min) + str(format(offset_formatted)),
        "timeMax": date + 'T' + str(datetime.time.max) + str(format(offset_formatted)),
        "timeZone": calendar_timezone,
        "items": [{"id": calendar_id}]
    }

    freebusy = service.freebusy().query(body=freebusy_query).execute()
    # print('freebusy: ', freebusy)
    freebusy_slots = freebusy['calendars'][calendar_id]['busy']
    # print('freebusy_slots:', freebusy_slots)
    free_slots = []
    for slot in freebusy_slots:
        start_time = slot['start']
        end_time = slot['end']
        free_slots.append((start_time, end_time))

    return free_slots
