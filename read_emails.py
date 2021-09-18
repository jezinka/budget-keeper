import logging
import re
from base64 import urlsafe_b64decode

from const import ME_ID, ID
from message import Message


def search_messages(service, label):
    result = service.users().messages().list(userId='me', labelIds=label).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    return messages


def read_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()

    payload = msg['payload']

    return process_message(payload)


def process_message(payload):
    headers = payload.get("headers")

    income = 'Wpływ' in list(filter(lambda x: x.get("name").lower() == "subject", headers))[0].get("value")
    receive_date = list(filter(lambda x: x.get("name").lower() == "date", headers))[0].get("value")

    body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
    body = re.sub(r'<.*>', '', body)
    body = re.sub(r'\s{2}', '', body)

    if income:
        m = re.search(r"Tytuł:(?P<tytul>[\w].*)Nadawca:(?P<kto>[\w].*)Kwota:(?P<kwota>[\d ]*,[\d]{2}) PLN", body)
    else:
        m = re.search(
            r"(Odbiorca:(?P<kto>.*))?Ile:(?P<kwota>[\d ]*,[\d]{2}) PLNTytuł:(?P<tytul>[\w].*)Kiedy:(?P<kiedy>[\d]{2}-[\d]{2}-[\d]{4})",
            body)
        if m is None:
            m = re.search(
                r"Ile:-?(?P<kwota>[\d ]*,[\d]{2}) PLNKiedy:(?P<kiedy>[\d]{2}-[\d]{2}-[\d]{4})Gdzie:(?P<tytul>[\w].*)Telefon",
                body)

    message = Message(m.groupdict(), income)
    logging.info(message.get_title())
    message.set_receive_date(receive_date)
    return message
