import logging
import time

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from dbutils import DbUtils
from fixedCostService import FixedCostService
from read_emails import search_bank_messages, read_message
from services import get_bank_gmail_service


def main():
    logging_config()
    gmail_service = get_bank_gmail_service()

    while True:
        results = search_bank_messages(gmail_service, LABEL_ID)

        logging.info(f'found {len(results)} mails for processing')
        if len(results) > 0:
            db_utils = DbUtils()
            fixed_cost_service = FixedCostService(db_utils)
            for msg in results:
                logging.info(f'message {msg[ID]} processing start')
                try:
                    message = read_message(gmail_service, msg)
                    logging.debug(f'message {msg[ID]} read')

                    category_id = db_utils.find_category(message.get_category())
                    db_utils.insert_transaction(message, category_id)
                    logging.debug(f'message {msg[ID]} saved in db')

                    gmail_service.users().messages().modify(userId=ME_ID,
                                                            id=msg[ID],
                                                            body={'removeLabelIds': [LABEL_ID]}
                                                            ).execute()
                    logging.debug(f'message {msg[ID]} label removed')
                    db_utils.insert_log('INFO', f"{str(message)}: saved successfully")

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
                    db_utils.insert_log('ERROR', message_log)
                    logging.info(f'message {msg[ID]} processing end')

            db_utils.close_connection()
        time.sleep(5 * 60)


if __name__ == "__main__":
    main()
