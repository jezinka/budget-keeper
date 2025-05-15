import logging
import time

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from gmail_service import get_bank_gmail_service
from rabbitMQ_communication import RabbitMQCommunication
from read_emails import search_bank_messages, read_message

MAX_RETRIES = 3

def process_messages(gmail_service, results):
    retries = {}

    with RabbitMQCommunication() as producer:
        for msg in results:
            msg_id = msg[ID]
            if retries.get(msg_id, 0) >= MAX_RETRIES:
                continue

            logging.info(f'message {msg_id} processing start')
            try:
                message = read_message(gmail_service, msg)
                logging.debug(f'message {msg_id} read')

                producer.send_expense_to_rabbitmq(message)
                logging.debug(f'message {msg_id} send to rabbitMQ')

                gmail_service.users().messages().modify(userId=ME_ID,
                                                        id=msg_id,
                                                        body={'removeLabelIds': [LABEL_ID]}
                                                        ).execute()
                logging.debug(f'message {msg_id} label removed')
                producer.send_log_to_rabbitmq('INFO', f"{str(message)}: saved successfully")

            except Exception as err:
                retries[msg_id] = retries.get(msg_id, 0) + 1
                if retries[msg_id] == MAX_RETRIES:
                    message_log = f"{msg_id}: {err} (failed after {MAX_RETRIES} attempts)"
                    logging.error(f"Unexpected error: {message_log}")
                    producer.send_log_to_rabbitmq('ERROR', f"Unexpected error: {message_log}")

            logging.info(f'message {msg_id} processing end')

def main():
    logging_config()

    while True:
        with get_bank_gmail_service() as gmail_service:
            results = search_bank_messages(gmail_service, LABEL_ID)

            logging.info(f'found {len(results)} mails for processing')

            if len(results) > 0:
                process_messages(gmail_service, results)

        time.sleep(5 * 60)


if __name__ == "__main__":
    main()
