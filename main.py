import openai
from create_event import create_event
from get_details import extract_attendees_list_from_user_prompt, extract_meeting_time_from_user_prompt, extract_meeting_date_from_user_prompt
from get_busy_slots import get_busy_slots
from get_common_free_slots import find_common_free_slots
import datetime
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from date_extract import convert_date_parameter

openai.api_key = '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'

# Define a global list variable to store messages
messages = []
meeting_title = None
meeting_date = None
meeting_time = None
meeting_attendees = []
creds = None

def get_api_response(prompt: str) -> str | None:
    text: str | None = None

    try:
        response: dict = openai.Completion.create(
            model='text-davinci-003',
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[' Human:', ' AI:']
        )

        choices: dict = response.get('choices')[0]
        text = choices.get('text')

    except Exception as e:
        print('ERROR:', e)

    return text


def update_list(message: str, pl: list[str]):
    pl.append(message)


# Create a prompt message containing the system data
def create_prompt(message: str, pl: list[str]) -> str:
    global messages
    # print('print', message)
    p_message: str = f'\nHuman: {message}'
    # print('print2', p_message)
    update_list(p_message, pl)

    messages.append(message)  # Add the message to the global list
    # print('all messages:', messages)
    prompt: str = ''.join(pl)
    # print('prompt', prompt)
    return prompt


# Creates a bot response
def get_bot_response(message: str, pl: list[str]) -> str:
    prompt: str = create_prompt(message, pl)
    # print('create_prompt', prompt)
    bot_response: str = get_api_response(prompt)
    # print('get_api_response', bot_response)
    if bot_response:
        update_list(bot_response, pl)
        pos: int = bot_response.find('\nAI: ')
        bot_response = bot_response[pos + 5:]
    else:
        bot_response = 'Something went wrong...'
    # print(bot_response)
    return bot_response


def authorization_setup():
    # OAuth 2.0 Setup
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file("cred.json", scopes=scopes)
    credentials = flow.run_local_server()

    pickle.dump(credentials, open("token.pkl", "wb"))
    global creds
    creds = pickle.load(open("token.pkl", "rb"))


system: str = open("system.txt").read()


def main():
    prompt_list: list[str] = ['You are an autobot from Transformers and will respond with different name everytime.',
                              '\nHuman: Hi',
                              '\nAI: Hi. How can I help you today?']

    while True:
        user_input: str = input('You: ')
        # print('user_input', user_input)

        common_free_slots = []

        if 'schedule a meeting' in user_input.lower():
            # print('Entering the if condition')
            prompt_list.append(system)

            global meeting_date
            meeting_date = extract_meeting_date_from_user_prompt(user_input)
            # print('meeting_date_value: ', meeting_date)

            global meeting_attendees
            meeting_attendees.append(extract_attendees_list_from_user_prompt(user_input))
            prompt_list.append(str(meeting_attendees))
            # global meeting_title
            # meeting_title.append(f"Meeting with {meeting_attendees}")

            authorization_setup()

            person1_busy_slots = []
            for attendee in meeting_attendees:
                email_address = attendee[0]
                person1_busy_slots = get_busy_slots(email_address, convert_date_parameter(meeting_date), creds)

            # Get your all available time slots
            person2_busy_slots = get_busy_slots('akansharawat2728@gmail.com', convert_date_parameter(meeting_date), creds)

            start_time = '2023-04-11T11:00:00+05:30'
            end_time = '2023-04-11T19:00:00+05:30'
            common_free_slots = find_common_free_slots(person1_busy_slots, person2_busy_slots, start_time, end_time)
            # print(common_free_slots)

        global meeting_time
        if meeting_time is not None:
            updated_meeting_time = extract_meeting_time_from_user_prompt(user_input)
            if updated_meeting_time is not None:
                meeting_time = updated_meeting_time
                # print('New meeting time:', meeting_time)

        if not meeting_time:
            # Extract time using dateutil
            meeting_time = extract_meeting_time_from_user_prompt(user_input)
            # print('meeting_time:', meeting_time)

        if meeting_time is not None:
            prompt_list.append(str(meeting_time))
            # response = f'Here are the meeting details:\nAttendees\' List: {meeting_attendees}\nDate: {meeting_date}\nTime: {meeting_time}\nPlease confirm.'

        response: str = get_bot_response(user_input, prompt_list)

        if len(common_free_slots) != 0:
            # print('enter 2nd if')
            # Initialize common_free_slots_str as an empty string
            common_free_slots_str = ""

            # Convert list of tuples to a list of strings
            for slot in common_free_slots:
                start_time, end_time = slot
                common_free_slots_str += f"{start_time} - {end_time}, \n"

            # Remove the trailing comma and space
            common_free_slots_str = common_free_slots_str.rstrip(", ")

            # Update response string
            response = f'Here is the list of common free slots:\n{common_free_slots_str}Please confirm the time slot.'

        if 'confirm' in user_input.lower() or 'ok' in user_input.lower() or 'yes' in user_input.lower():
            # print('enter')
            start_time_str = meeting_date + ' ' + meeting_time
            create_event(start_time_str, f"Meeting with {meeting_attendees}", meeting_attendees, creds)

        print(f'Bot: {response}')


if __name__ == '__main__':
    main()

# schedule a meeting with akansharawat.ind@gmail.com tomorrow