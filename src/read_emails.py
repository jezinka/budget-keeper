import html
import json
import logging
import re
from base64 import urlsafe_b64decode
from datetime import datetime

from bs4 import BeautifulSoup

from const import ME_ID, ID, AMOUNT_KEY, CURRENCY_KEY, TITLE_KEY, WHO_KEY, WHEN_KEY, INCOME_KEY, LONG_F
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
    def extract_required(pattern, field_name):
        match = re.search(pattern, body, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not parse {field_name} from email body")
        return match.group(field_name)

    amount = extract_required(
        rf"(?:Ile|Kwota):\s*[\+\-]?(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}})",
        AMOUNT_KEY,
    )
    currency = extract_required(
        rf"(?:Ile|Kwota):\s*[\+\-]?[\d ]*,\d{{2}}\s*(?P<{CURRENCY_KEY}>[A-Z]{{3}})",
        CURRENCY_KEY,
    )

    when_match = re.search(rf"Kiedy:\s*(?P<{WHEN_KEY}>\d{{2}}-\d{{2}}-\d{{4}})", body)
    title_match = re.search(
        rf"(?:Tytuł|Gdzie):\s*(?P<{TITLE_KEY}>.*?)(?=\s*(?:Nadawca:|Odbiorca:|Od kogo:|Do kogo:|Kwota:|Ile:|Kiedy:|Data księgowania:|Na konto:|Saldo:|Tel|$))",
        body,
    )
    who_match = re.search(
        rf"(?:Nadawca|Odbiorca|Od kogo|Do kogo):\s*(?P<{WHO_KEY}>.*?)(?=\s*(?:Kwota:|Ile:|Tytuł:|Kiedy:|Data księgowania:|Na konto:|Saldo:|Tel|$))",
        body,
    )

    if not title_match:
        raise ValueError("Could not parse title from email body")

    message_dict = {
        AMOUNT_KEY: amount,
        CURRENCY_KEY: currency,
        TITLE_KEY: title_match.group(TITLE_KEY).strip(),
        WHO_KEY: who_match.group(WHO_KEY).strip() if who_match else None,
        INCOME_KEY: income,
    }
    if when_match:
        message_dict[WHEN_KEY] = when_match.group(WHEN_KEY)

    return message_dict


def is_income(body, headers):
    title = next(header.get("value") for header in headers if header.get("name").lower() == "subject")
    income = bool(re.search('Wpływ|Wpłata', title)) or bool(re.search(rf"Ile:\+(?P<{AMOUNT_KEY}>[\d ]*,\d{{2}})", body))
    return income


def prepare_body(payload):
    body = urlsafe_b64decode(payload.get("body")['data']).decode("utf-8", "replace")
    text = BeautifulSoup(body, 'html.parser').table.table.get_text().strip()
    return re.sub(r'\s{2}', '', text)


def read_purchase_info_message(service, mail):
    msg = service.users().messages().get(userId=ME_ID, id=mail[ID], format='full').execute()
    headers = msg['payload'].get('headers', [])
    html_body = extract_html_body(msg['payload'])
    jsonld_items = extract_jsonld_from_html(html_body)
    if jsonld_items:
        return parse_purchase_info(jsonld_items, html_body)
    return parse_donation(headers)


def extract_html_body(payload):
    if payload.get('mimeType') == 'text/html':
        data = payload.get('body', {}).get('data', '')
        if data:
            return urlsafe_b64decode(data).decode('utf-8', 'replace')
    for part in payload.get('parts', []):
        result = extract_html_body(part)
        if result:
            return result
    return ''


def parse_purchase_info(jsonld_items, html_body=''):
    flat_items = []
    for item in jsonld_items:
        if isinstance(item, list):
            flat_items.extend(item)
        else:
            flat_items.append(item)

    order = next((item for item in flat_items if isinstance(item, dict) and item.get('@type') == 'Order'), None)
    if order is None:
        raise ValueError("No Order found in ld+json")

    order_date = order.get('orderDate')
    accepted_offers = order.get('acceptedOffer', [])
    names = [offer.get('itemOffered', {}).get('name', '') for offer in accepted_offers if isinstance(offer, dict)]

    price = _extract_blik_payment(html_body) or order.get('price')

    return {
        'price': price,
        'name': ', '.join(filter(None, names)),
        'orderDate': order_date
    }


def _extract_blik_payment(html_body):
    """Extract actual BLIK payment amount from email HTML body.
    Handles cases where points/vouchers reduce the amount paid vs. the order total."""
    soup = BeautifulSoup(html_body, 'html.parser')
    text = soup.get_text(separator=' ')
    match = re.search(r'Płatność\s+([\d\s]+,\d{2})\s*zł', text)
    if match:
        return match.group(1).replace(' ', '').replace(',', '.')
    return None


def parse_donation(headers):
    """Parse donation confirmation email
    Extracts amount and organization from subject, date from email header."""

    def get_header(name):
        return next((h['value'] for h in headers if h['name'].lower() == name.lower()), '')

    subject = get_header('subject')
    date_str = get_header('date')

    amount_match = re.search(r'darowizna\s+([\d]+(?:[,.]\d+)?)\s*zł', subject)
    if not amount_match:
        raise ValueError(f"Could not parse donation amount from subject: {subject}")
    price = amount_match.group(1).replace(',', '.')

    org_match = re.search(r'została przekazana\s*[-–]\s*(.+)$', subject)
    if not org_match:
        raise ValueError(f"Could not parse organization from subject: {subject}")
    name = org_match.group(1).strip()

    date = datetime.strptime(date_str, LONG_F)
    order_date = date.strftime('%-d.%m.%Y, %H:%M')

    return {'price': price, 'name': name, 'orderDate': order_date}


def extract_jsonld_from_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        content = script.string if script.string is not None else script.get_text()
        if not content:
            continue
        content = html.unescape(content).strip()
        try:
            parsed = json.loads(content)
            results.append(parsed)
        except json.JSONDecodeError as e:
            results.append({"_raw": content, "_error": str(e)})
    return results
