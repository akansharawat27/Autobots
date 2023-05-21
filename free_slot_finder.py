import datetime
from googleapiclient.discovery import build
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from get_busy_slots import get_busy_slots


def remove_colon_from_timezone_offset(time_str):
    # Extract timezone offset from the input string
    offset_str = time_str[-6:]
    # Remove colons from the timezone offset
    offset_str = offset_str[:3] + offset_str[4:]
    # Replace timezone offset in the input string
    time_str = time_str[:-6] + offset_str
    return time_str


def find_free_slots(calendar_id, meeting_date, creds):

    # Get busy_slots
    busy_slots = get_busy_slots(calendar_id, meeting_date, creds)

    # Convert input string to datetime objects
    start_time = datetime.datetime.strptime(remove_colon_from_timezone_offset(meeting_date + 'T11:00:00+05:30'),
                                            "%Y-%m-%dT%H:%M:%S%z")
    end_time = datetime.datetime.strptime(remove_colon_from_timezone_offset(meeting_date + 'T19:00:00+05:30'),
                                          "%Y-%m-%dT%H:%M:%S%z")

    busy_slots = [
        (datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[0]), "%Y-%m-%dT%H:%M:%S%z"),
         datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[1]), "%Y-%m-%dT%H:%M:%S%z"))
        for slot in busy_slots]

    # Generate the list of common free slots in 1-hour intervals
    common_free_slots = []
    current_time = start_time
    while current_time < end_time:
        slot_start = current_time
        slot_end = current_time + datetime.timedelta(hours=1)
        slot = (slot_start.strftime("%Y-%m-%dT%H:%M:%S%z"), slot_end.strftime("%Y-%m-%dT%H:%M:%S%z"))

        person_is_free = True
        for event_slot in busy_slots:
            if slot_start >= event_slot[0] and slot_start < event_slot[1]:
                person_is_free = False
                break
            elif slot_end > event_slot[0] and slot_end <= event_slot[1]:
                person_is_free = False
                break
            elif slot_start <= event_slot[0] and slot_end >= event_slot[1]:
                person_is_free = False
                break
        if person_is_free:
            common_free_slots.append(slot)
        current_time += datetime.timedelta(hours=1)

    return common_free_slots
