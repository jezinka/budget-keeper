import logging

from const import SPREAD_KEY, months


def write_messages(spread_service, m):
    sheet = spread_service.open_by_key(SPREAD_KEY).worksheet(get_worksheet_name(m))
    row_index = get_first_empty_row(sheet)

    logging.debug(f'Writing message {m.get_title()} into row {row_index}')

    sheet.update_cell(row_index, 1, m.get_date())
    sheet.update_cell(row_index, 2, m.get_title())
    sheet.update_cell(row_index, 3, m.get_who())
    sheet.update_cell(row_index, 4, m.get_amount())
    sheet.update_cell(row_index, 6, m.get_category())


def get_worksheet_name(m):
    month_no = m.get_month()
    return months[month_no - 1]


def get_first_empty_row(sheet):
    values = sheet.col_values(1)
    return len(values) + 1
