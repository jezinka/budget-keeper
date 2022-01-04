import logging

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from read_emails import search_bank_messages, read_message
from services import get_gspread_service, get_bank_gmail_service
from write_spread import write_messages

if __name__ == "__main__":
    logging_config()
    gmail_service = get_bank_gmail_service()
    spread_service = get_gspread_service()

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

                gmail_service.users().messages().modify(userId=ME_ID,
                                                        id=msg[ID],
                                                        body={'removeLabelIds': [LABEL_ID]}
                                                        ).execute()
                logging.debug(f'message {msg[ID]} label removed')

            except Exception as err:
                logging.error(f"Unexpected error: {msg[ID]}: {err}")
                logging.info(f'message {msg[ID]} processing end')
