import logging
import re
from base64 import urlsafe_b64decode

from bs4 import BeautifulSoup

from const import ME_ID, ID, AMOUNT_KEY, CURRENCY_KEY, TITLE_KEY, WHO_KEY, WHEN_KEY, INCOME_KEY
from message import Message


def search_bank_messages(service, label):
    result = service.users().messages().list(userId='me', labelIds=label).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    return messages


def read_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()
    return process_message(msg['payload'])


def process_message(payload):
    headers = payload.get("headers")
    body = prepare_body(payload)
    income = is_income(body, headers)

    receive_date = list(filter(lambda x: x.get("name").lower() == "date", headers))[0].get("value")

    message_dict = prepare_message_dict(body, income)

    message = Message(message_dict)
    logging.info(message.get_title())
    message.set_receive_date(receive_date)
    return message


def prepare_message_dict(body, income):
    m = re.search(
        rf"Ile:[\+\-]?(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}}) Kiedy:(?P<{WHEN_KEY}>\d{{2}}-\d{{2}}-\d{{4}})([\w ].*)Gdzie:(?P<{TITLE_KEY}>\w.*)Tel",
        body)

    if m is None:
        if income:
            m = re.search(
                rf"Tytuł:(?P<{TITLE_KEY}>\w.*)Nadawca:(?P<{WHO_KEY}>\w.*)Kwota:(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}})",
                body)
        else:
            m = re.search(
                rf"(Odbiorca:(?P<{WHO_KEY}>.*))? Ile:(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}}) (?P<{CURRENCY_KEY}>\w{{3}}) Tytuł:(?P<{TITLE_KEY}>.*) Kiedy:(?P<{WHEN_KEY}>\d{{2}}-\d{{2}}-\d{{4}})",
                body)

    m_groupdict = m.groupdict()
    m_groupdict[INCOME_KEY] = income
    return m_groupdict


def is_income(body, headers):
    title = list(filter(lambda x: x.get("name").lower() == "subject", headers))[0].get("value")
    income = re.search('Wpływ|Wpłata', title) is not None
    if not income:
        income = re.search(rf"Ile:\+(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}})", body) is not None
    return income


def prepare_body(payload):
    body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.table.table.get_text().strip()
    return re.sub(r'\s{2}', '', text)
