import logging
import re
from base64 import urlsafe_b64decode

from bs4 import BeautifulSoup

from const import ME_ID, ID, AMOUNT_KEY, CURRENCY_KEY, TITLE_KEY, WHO_KEY, WHEN_KEY, INCOME_KEY
from message import Message


def search_bank_messages(service, label):
    result = service.users().messages().list(userId='me', labelIds=label).execute()
    return result.get('messages', [])


def read_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()
    return process_message(msg['payload'])


def process_message(payload):
    headers = payload.get("headers")
    body = prepare_body(payload)
    income = is_income(body, headers)
    receive_date = next(header.get("value") for header in headers if header.get("name").lower() == "date")
    message_dict = prepare_message_dict(body, income)
    message = Message(message_dict)
    logging.info(message.get_title())
    message.set_receive_date(receive_date)
    return message


def prepare_message_dict(body, income):
    patterns = [
        rf"Ile:[\+\-]?(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}}) Kiedy:(?P<{WHEN_KEY}>\d{{2}}-\d{{2}}-\d{{4}})([\w ].*)Gdzie:(?P<{TITLE_KEY}>[\w\"].*)Tel",
        rf"Tytuł:(?P<{TITLE_KEY}>.+?)Nadawca:(?P<{WHO_KEY}>\w.*)Kwota:(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}})",
        rf"(Odbiorca:(?P<{WHO_KEY}>.*))? Ile:(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}}) Tytuł:(?P<{TITLE_KEY}>.*) Kiedy:(?P<{WHEN_KEY}>\d{{2}}-\d{{2}}-\d{{4}})"
    ]
    m = None
    for pattern in patterns:
        m = re.search(pattern, body)
        if m:
            break

    if m is None:
        raise ValueError("No match found in the email body")

    m_groupdict = m.groupdict()
    m_groupdict[INCOME_KEY] = income
    return m_groupdict


def is_income(body, headers):
    title = next(header.get("value") for header in headers if header.get("name").lower() == "subject")
    income = bool(re.search('Wpływ|Wpłata', title)) or bool(re.search(rf"Ile:\+(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}})", body))
    return income


def prepare_body(payload):
    body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
    text = BeautifulSoup(body, 'html.parser').table.table.get_text().strip()
    return re.sub(r'\s{2}', '', text)
