from datetime import datetime

import const
from category import get_category
from const import DATE_KEY, WHEN_KEY, INCOME_KEY, AMOUNT_KEY, WHO_KEY, TITLE_KEY, SPREAD_KEY


def write_messages(spread_service, m):
    sheet = spread_service.open_by_key(SPREAD_KEY).worksheet(get_worksheet_name(m))

    row_index = get_first_empty_row(sheet)
    sheet.update_cell(row_index, 1, get_date(m))
    title = m[TITLE_KEY]

    sheet.update_cell(row_index, 2, title)
    sheet.update_cell(row_index, 3, get_who(m))
    sheet.update_cell(row_index, 4, get_amount(m))
    sheet.update_cell(row_index, 7, get_category(get_who(m), title))


def get_worksheet_name(m):
    return const.months[8]


def get_who(m):
    return m[WHO_KEY] if WHO_KEY in m and m[WHO_KEY] is not None else ''


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
