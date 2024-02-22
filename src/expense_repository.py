from model import Expense


def create_expense(category, message):
    Expense.create(transaction_date=message.get_date(), title=message.get_title(),
                   payee=message.get_who(),
                   amount=message.get_amount(to_string=False), category=category,
                   automatic_category=category is not None)
