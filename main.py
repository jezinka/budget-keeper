import logging
import sys

import categorize
import clean_messages
from const import LABEL_ID, ME_ID, ID
from read_emails import search_bank_messages, read_message, finding_corresponding_mails
from services import get_gspread_service, get_bank_gmail_service, get_message_gmail_service
from write_csv import write_to_input, write_to_history, delete_file
from write_spread import write_messages

if __name__ == "__main__":
    file_handler = logging.FileHandler(filename='logs/bk.log')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(handlers=handlers, datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
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

                if 'kartą' in message.get_title().lower() or 'blik' in message.get_title().lower():
                    gmail_message_service = get_message_gmail_service()
                    body = finding_corresponding_mails(gmail_message_service, message, msg[ID])

                    if len(body) > 0:
                        message.tokens = ';'.join(clean_messages.process_body(body))
                        logging.debug(f'message {msg[ID]} tokenized corresponding mails')

                write_to_input(message)
                logging.debug(f'message {msg[ID]} saved in input for ludwig')

                category = categorize.predict()
                logging.debug(f'message {msg[ID]} predicted category: {category}')
                message.set_category(category)

                write_to_history(message)
                logging.debug(f'message {msg[ID]} saved in csv')

                write_messages(spread_service, message)
                logging.debug(f'message {msg[ID]} saved in sheet')

                gmail_service.users().messages().modify(userId=ME_ID, id=msg[ID],
                                                        body={'removeLabelIds': [LABEL_ID]}).execute()
                logging.debug(f'message {msg[ID]} label removed')

            except Exception as err:
                logging.error(f"Unexpected error: {msg[ID]}")
                logging.info(f'message {msg[ID]} processing end')
            finally:
                delete_file()
                logging.debug('input file deleted')
