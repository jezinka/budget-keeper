import logging
import re
from base64 import urlsafe_b64decode
from datetime import datetime, timedelta

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


def get_mail_query(date, amount):
    date = datetime.strptime(date, "%d-%m-%Y")
    day_before = f'after: {(date - timedelta(days=1)).strftime("%Y/%m/%d")}'
    day_after = f'before: {(date + timedelta(days=1)).strftime("%Y/%m/%d")}'
    return f'"{amount}" -"Poszerz swoje ostatnie zakupy" -"pożegnaliśmy Twoją paczuszkę" {day_before} {day_after}'


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


def finding_corresponding_mails(gmail_message_service, message, msg_id):
    date = message.get_date()
    amount = re.sub(r'-', '', message.get_amount())
    corresponding_body = get_mails(amount, date, gmail_message_service, msg_id)
    if len(corresponding_body) == 0:
        amount = re.sub(r',', '.', amount)
        corresponding_body = get_mails(amount, date, gmail_message_service, msg_id)
    if len(corresponding_body) == 0 and len(amount) > 6:
        amount = amount[:-6] + '.' + amount[-6:]
        corresponding_body = get_mails(amount, date, gmail_message_service, msg_id)
    return corresponding_body


def get_mails(amount, date, gmail_message_service, msg_id):
    body = search_mails(gmail_message_service, get_mail_query(date, amount))
    result = "found something" if len(body) > 0 else "nothing"
    logging.debug(f'message {msg_id} searching for corresponding mails - {result}')
    return body
