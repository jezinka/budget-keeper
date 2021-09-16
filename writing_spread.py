from datetime import datetime

import gspread

from category import get_category
from const import DATE_KEY, WHEN_KEY, INCOME_KEY, AMOUNT_KEY, WHO_KEY, TITLE_KEY


def connect_to_spreadsheet():
    # connect to google sheet
    google_spread_oauth = gspread.oauth()
    return google_spread_oauth


def write_messages(sheet, m):
    row_index = get_first_empty_row(sheet)
    sheet.update_cell(row_index, 1, get_date(m))
    title = m[TITLE_KEY]

    sheet.update_cell(row_index, 2, title)
    sheet.update_cell(row_index, 3, get_who(m))
    sheet.update_cell(row_index, 4, get_amount(m))
    sheet.update_cell(row_index, 7, get_category(get_who(m), title))


def get_who(m):
    if WHO_KEY in m and m[WHO_KEY] is not None:
        return m[WHO_KEY]
    return ''


def get_amount(m):
    amount = float(m[AMOUNT_KEY].replace(',', '.').replace(' ', ''))
    return amount if m[INCOME_KEY] else (amount * -1)


def get_first_empty_row(sheet):
    values = sheet.col_values(1)
    return len(values) + 1


def get_date(m):
    short_f = "%d-%m-%Y"
    long_f = "%a, %d %b %Y %H:%M:%S %z"
    date = datetime.strptime(m[WHEN_KEY], short_f) if WHEN_KEY in m else datetime.strptime(m[DATE_KEY], long_f)
    return date.strftime(short_f)
