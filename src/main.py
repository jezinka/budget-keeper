import logging
import time

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from gmail_service import get_bank_gmail_service
from read_emails import search_bank_messages, read_message
from src.repository.category_repository import get_category_by_name
from src.repository.expense_repository import create_expense
from src.repository.log_repository import create_log
from src.service.fixed_cost_service import FixedCostService


def main():
    logging_config()
    gmail_service = get_bank_gmail_service()
    fixed_cost_service = FixedCostService()

    while True:
        results = search_bank_messages(gmail_service, LABEL_ID)

        logging.info(f'found {len(results)} mails for processing')
        if len(results) > 0:
            for msg in results:
                logging.info(f'message {msg[ID]} processing start')
                try:
                    message = read_message(gmail_service, msg)
                    logging.debug(f'message {msg[ID]} read')

                    category = get_category_by_name(message.get_category())
                    create_expense(category, message)
                    logging.debug(f'message {msg[ID]} saved in db')

                    gmail_service.users().messages().modify(userId=ME_ID,
                                                            id=msg[ID],
                                                            body={'removeLabelIds': [LABEL_ID]}
                                                            ).execute()
                    logging.debug(f'message {msg[ID]} label removed')
                    create_log('INFO', f"{str(message)}: saved successfully")

                    logging.info(f'message {msg[ID]} checking fixed cost start')
                    fixed_cost = fixed_cost_service.check(message)
                    if fixed_cost is None:
                        logging.info(f'message {msg[ID]} not a fixed cost')
                    else:
                        logging.info(f'message {msg[ID]} is a fixed cost')
                        fixed_cost_service.mark_as_payed(fixed_cost, message)
                    logging.info(f'message {msg[ID]} checking fixed cost end')

                except Exception as err:
                    message_log = f"{msg[ID]}: {err}"
                    logging.error(f"Unexpected error: {message_log}")
                    create_log('ERROR', f"Unexpected error: {message_log}")

                logging.info(f'message {msg[ID]} processing end')

        time.sleep(5)


if __name__ == "__main__":
    main()
