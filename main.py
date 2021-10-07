import logging

from const import LABEL_ID, ME_ID, ID
from read_emails import search_messages, read_message
from services import get_gmail_service, get_gspread_service
from write_csv import write_to_csv
from write_spread import write_messages

if __name__ == "__main__":
    logging.basicConfig(filename='logs/bk.log', filemode='a', level=logging.INFO)
    gmail_service = get_gmail_service()
    spread_service = get_gspread_service()

    results = search_messages(gmail_service, LABEL_ID)

    logging.info(f'found {len(results)} mails for processing\n')
    if len(results) > 0:
        for msg in results:
            logging.info(f'message {msg[ID]} processing start')
            try:
                message = read_message(gmail_service, msg)
                logging.debug(f'message {msg[ID]} read')
                write_messages(spread_service, message)
                logging.debug(f'message {msg[ID]} saved in sheet')
                write_to_csv(message)
                logging.debug(f'message {msg[ID]} saved in csv')
                gmail_service.users().messages().modify(userId=ME_ID, id=msg[ID],
                                                        body={'removeLabelIds': [LABEL_ID]}).execute()
                logging.debug(f'message {msg[ID]} label removed')

            except:
                logging.error("Unexpected error: {msg['id']")
            logging.info(f'message {msg[ID]} processing end\n')
