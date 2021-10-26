import re
from datetime import datetime

from const import AMOUNT_KEY, TITLE_KEY, WHO_KEY, WHEN_KEY, SHORT_F, LONG_F


class Message:
    title = None
    who = None
    amount = None
    operation_date = None  # when

    receive_date = None  # date
    tokens = None
    category = None

    def __init__(self, mail_dict, income):
        self.title = mail_dict[TITLE_KEY]
        self.set_who(mail_dict)
        self.set_amount(mail_dict[AMOUNT_KEY], income)
        self.set_operation_date(mail_dict)

    def set_amount(self, amount, income):
        amount = float(amount.replace(',', '.').replace(' ', ''))
        self.amount = amount if income else (amount * -1)

    def set_who(self, mail_dict):
        self.who = mail_dict[WHO_KEY] if WHO_KEY in mail_dict and mail_dict[WHO_KEY] is not None else ''

    def set_operation_date(self, mail_dict):
        self.operation_date = datetime.strptime(mail_dict[WHEN_KEY], SHORT_F) if WHEN_KEY in mail_dict else None

    def set_receive_date(self, receive_date):
        self.receive_date = datetime.strptime(receive_date, LONG_F)

    def set_tokens(self, tokens):
        self.tokens = tokens

    def set_category(self, category):
        self.category = category

    def get_date(self):
        date = self.operation_date if self.operation_date is not None else self.receive_date
        return date.strftime(SHORT_F)

    def get_title(self):
        return self.title

    def get_who(self):
        return self.who

    def get_amount(self):
        string_amount = "{:.2f}".format(self.amount)
        return re.sub(r'\.', ',', string_amount)

    def get_month(self):
        date = self.operation_date if self.operation_date is not None else self.receive_date
        return int(date.strftime('%m'))

    def get_tokens(self):
        return self.tokens

    def get_category(self):
        return self.category

    def get_row(self):
        return [self.get_date(), self.get_title(), self.get_who(), self.get_amount(), self.get_tokens()]

    def get_row_with_category(self):
        return [self.get_date(), self.get_title(), self.get_who(), self.get_amount(), self.get_tokens(),
                self.get_category()]
