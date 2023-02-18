import re
from datetime import datetime
from const import AMOUNT_KEY, CURRENCY_KEY, TITLE_KEY, INCOME_KEY, PLN, WHO_KEY, WHEN_KEY, SHORT_F, LONG_F
from forex_python.converter import CurrencyRates


class Message:
    title = None
    who = None
    amount = None
    operation_date = None  # when

    receive_date = None  # date

    def __init__(self, mail_dict):
        self.title = mail_dict[TITLE_KEY]
        self.set_who(mail_dict)
        self.set_amount(mail_dict)
        self.set_operation_date(mail_dict)

    def __str__(self):
        log_message = self.title
        if not (self.who is None):
            log_message += ' ' + self.who
        log_message += ': ' + self.get_amount()
        return log_message

    def set_amount(self, m_dict):
        amount = float(m_dict[AMOUNT_KEY].replace(',', '.').replace(' ', ''))
        currency = m_dict[CURRENCY_KEY]
        if currency != PLN:
            c = CurrencyRates()
            amount *= c.get_rate(currency, PLN)
        self.amount = amount if m_dict[INCOME_KEY] else (amount * -1)

    def set_who(self, mail_dict):
        self.who = mail_dict[WHO_KEY] if WHO_KEY in mail_dict and mail_dict[WHO_KEY] is not None else ''

    def set_operation_date(self, mail_dict):
        self.operation_date = datetime.strptime(mail_dict[WHEN_KEY], SHORT_F) if WHEN_KEY in mail_dict else None

    def set_receive_date(self, receive_date):
        self.receive_date = datetime.strptime(receive_date, LONG_F)

    def get_date(self):
        date = self.operation_date if self.operation_date is not None else self.receive_date
        return date.strftime(SHORT_F)

    def get_title(self):
        return self.title

    def get_who(self):
        return self.who

    def get_amount(self, to_string=True):
        if to_string is True:
            string_amount = "{:.2f}".format(self.amount)
            return re.sub(r'\.', ',', string_amount)
        else:
            return self.amount

    def get_month(self):
        date = self.operation_date if self.operation_date is not None else self.receive_date
        return int(date.strftime('%m'))

    def get_category(self):
        if self.title is None:
            return ''

        if 'końcówek' in self.title:
            return 'końcówki'
        if 'IKZE' in self.title:
            return 'emerytura'
        if 'Legimi' in self.title or 'Doładowanie telefonu' in self.title or 'spotify' in self.title.lower():
            return 'abonament'
        if 'Urbancard' in self.title:
            return 'bilety'
        if 'Finax' in self.who:
            return 'inwestycje'
        if 'Steam' in self.title:
            return 'gry'
        return ''

