import datetime


def remove_colon_from_timezone_offset(time_str):
    # Extract timezone offset from the input string
    offset_str = time_str[-6:]
    # Remove colons from the timezone offset
    offset_str = offset_str[:3] + offset_str[4:]
    # Replace timezone offset in the input string
    time_str = time_str[:-6] + offset_str
    return time_str


def find_common_free_slots(person1_busy_slots, person2_busy_slots, start_time, end_time):
    # Convert input string to datetime objects
    start_time = datetime.datetime.strptime(remove_colon_from_timezone_offset(start_time), "%Y-%m-%dT%H:%M:%S%z")
    end_time = datetime.datetime.strptime(remove_colon_from_timezone_offset(end_time), "%Y-%m-%dT%H:%M:%S%z")

    # Convert person1_busy_slots and person2_busy_slots to datetime objects with timezone information
    person1_busy_slots = [
        (datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[0]), "%Y-%m-%dT%H:%M:%S%z"),
         datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[1]), "%Y-%m-%dT%H:%M:%S%z"))
        for slot in person1_busy_slots]
    person2_busy_slots = [
        (datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[0]), "%Y-%m-%dT%H:%M:%S%z"),
         datetime.datetime.strptime(remove_colon_from_timezone_offset(slot[1]), "%Y-%m-%dT%H:%M:%S%z"))
        for slot in person2_busy_slots]

    # Generate the list of common free slots in 1-hour intervals
    common_free_slots = []
    current_time = start_time
    while current_time < end_time:
        slot_start = current_time
        slot_end = current_time + datetime.timedelta(hours=1)
        slot = (slot_start.strftime("%Y-%m-%dT%H:%M:%S%z"), slot_end.strftime("%Y-%m-%dT%H:%M:%S%z"))

        person1_is_free = True
        for event_slot in person1_busy_slots:
            if slot_start >= event_slot[0] and slot_start < event_slot[1]:
                person1_is_free = False
                break
            elif slot_end > event_slot[0] and slot_end <= event_slot[1]:
                person1_is_free = False
                break
            elif slot_start <= event_slot[0] and slot_end >= event_slot[1]:
                person1_is_free = False
                break

        person2_is_free = True
        for event_slot in person2_busy_slots:
            if slot_start >= event_slot[0] and slot_start < event_slot[1]:
                person2_is_free = False
                break
            elif slot_end > event_slot[0] and slot_end <= event_slot[1]:
                person2_is_free = False
                break
            elif slot_start <= event_slot[0] and slot_end >= event_slot[1]:
                person2_is_free = False
                break

        if person1_is_free and person2_is_free:
            common_free_slots.append(slot)

        current_time += datetime.timedelta(hours=1)

    return common_free_slots
