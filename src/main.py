import logging
import time

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from gmail_service import get_bank_gmail_service
from kafka_communication import KafkaCommunication
from read_emails import search_bank_messages, read_message


def main():
    logging_config()
    kafka_producer = KafkaCommunication()
    gmail_service = get_bank_gmail_service()
    while True:
        results = search_bank_messages(gmail_service, LABEL_ID)

        logging.info(f'found {len(results)} mails for processing')

        if len(results) > 0:
            for msg in results:
                logging.info(f'message {msg[ID]} processing start')
                try:
                    message = read_message(gmail_service, msg)
                    logging.debug(f'message {msg[ID]} read')
                    kafka_producer.send_expense_to_kafka(message)
                    logging.debug(f'message {msg[ID]} send to kafka')

                    gmail_service.users().messages().modify(userId=ME_ID,
                                                            id=msg[ID],
                                                            body={'removeLabelIds': [LABEL_ID]}
                                                            ).execute()
                    logging.debug(f'message {msg[ID]} label removed')
                    kafka_producer.send_log_to_kafka('INFO', f"{str(message)}: saved successfully")

                except Exception as err:
                    message_log = f"{msg[ID]}: {err}"
                    logging.error(f"Unexpected error: {message_log}")
                    kafka_producer.send_log_to_kafka('ERROR', f"Unexpected error: {message_log}")

                logging.info(f'message {msg[ID]} processing end')

        time.sleep(5 * 60)


if __name__ == "__main__":
    main()
