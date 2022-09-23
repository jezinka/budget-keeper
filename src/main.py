import logging
import time

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from dbutils import DbUtils
from read_emails import search_bank_messages, read_message
from services import get_gspread_service, get_bank_gmail_service
from write_spread import write_messages


def main():
    logging_config()
    gmail_service = get_bank_gmail_service()
    spread_service = get_gspread_service()
    db_utils = DbUtils()

    while True:
        results = search_bank_messages(gmail_service, LABEL_ID)

        logging.info(f'found {len(results)} mails for processing')
        if len(results) > 0:
            for msg in results:
                logging.info(f'message {msg[ID]} processing start')
                try:
                    message = read_message(gmail_service, msg)
                    logging.debug(f'message {msg[ID]} read')

                    write_messages(spread_service, message)
                    logging.debug(f'message {msg[ID]} saved in sheet')

                    db_utils.insert_transaction(message)
                    logging.debug(f'message {msg[ID]} saved in db')

                    gmail_service.users().messages().modify(userId=ME_ID,
                                                            id=msg[ID],
                                                            body={'removeLabelIds': [LABEL_ID]}
                                                            ).execute()
                    logging.debug(f'message {msg[ID]} label removed')

                except Exception as err:
                    logging.error(f"Unexpected error: {msg[ID]}: {err}")
                    logging.info(f'message {msg[ID]} processing end')

                    db_utils.close_connection()
        time.sleep(5 * 60)


if __name__ == "__main__":
    main()
