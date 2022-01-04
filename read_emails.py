import logging
import re
from base64 import urlsafe_b64decode

from const import ME_ID, ID
from message import Message


def search_bank_messages(service, label):
    result = service.users().messages().list(userId='me', labelIds=label).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    return messages


def parse_message(payload):
    message_body = ''
    if 'data' in payload.get("body"):
        message_body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
        message_body = re.sub(r'\s{2}', '', message_body)
    else:
        if payload.get("parts"):
            desired_mime_types = ['multipart/alternative', 'multipart/mixed', 'multipart/related', 'text/plain',
                                  'text/html']
            parts = list(filter(
                lambda x: x.get('mimeType') in desired_mime_types, payload['parts']))
            if len(parts) == 0:
                logging.error(';'.join([d['mimeType'] for d in payload['parts']]))
            for part in parts:
                return parse_message(part)
    return message_body


def search_mails(service, query):
    print(query)
    result = service.users().messages().list(userId=ME_ID, q=query).execute()
    if result.get('resultSizeEstimate') == 0:
        return []
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])

    mails_body = []
    for msg in messages:
        mail = service.users().messages().get(userId=ME_ID, id=msg[ID], format='full').execute()
        payload = mail['payload']
        mails_body.append(parse_message(payload))

    return '\n'.join(mails_body)


def read_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()
    return process_message(msg['payload'])


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
