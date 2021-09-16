import re
from base64 import urlsafe_b64decode

from common import gmail_authenticate, search_messages
from const import LABEL_ID, WORKSHEET_NAME, SPREAD_KEY, ME_ID, ID, INCOME_KEY, DATE_KEY
from writing_spread import connect_to_spreadsheet, write_messages


def read_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()

    payload = msg['payload']
    headers = payload.get("headers")

    income = 'Wpływ' in list(filter(lambda x: x.get("name").lower() == "subject", headers))[0].get("value")
    receive_date = list(filter(lambda x: x.get("name").lower() == "date", headers))[0].get("value")

    body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
    body = re.sub(r'<.*>', '', body)
    body = re.sub(r'\s{2}', '', body)
    msg_dict = process_message(body, income)
    msg_dict[DATE_KEY] = receive_date
    msg_dict[INCOME_KEY] = income
    return msg_dict


def process_message(body, income):
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
    message_dict = m.groupdict()
    return message_dict


if __name__ == "__main__":
    service = gmail_authenticate()
    google_spread_oauth = connect_to_spreadsheet()
    sheet = google_spread_oauth.open_by_key(SPREAD_KEY).worksheet(WORKSHEET_NAME)

    results = search_messages(service, LABEL_ID)
    for msg in results:
        try:
            message = read_message(service, msg)
            write_messages(sheet, message)
            service.users().messages().modify(userId=ME_ID, id=msg[ID], body={'removeLabelIds': [LABEL_ID]}).execute()
        except:
            print("Unexpected error:", msg['id'])
