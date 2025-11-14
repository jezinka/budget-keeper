"""
Main application for processing bank transaction emails from Gmail.

This module fetches emails with a specific label, parses transaction details,
enriches them with receipt information, and publishes to RabbitMQ.

Features:
- Fetches bank transaction emails from Gmail
- Enriches transactions with detailed receipt information
- Searches for matching receipts based on date and amount
- Extracts item-level details from receipts
- Publishes enriched expense data to RabbitMQ
"""
import logging
import time
from decimal import Decimal

from budget_logging import logging_config
from const import LABEL_ID, ME_ID, ID
from gmail_service import get_bank_gmail_service
from rabbitMQ_communication import RabbitMQCommunication
from read_emails import search_bank_messages, read_message
from email_parser import extract_amount, extract_date
from email_searcher import EmailSearcher
from receipt_extractor import ReceiptExtractor

MAX_RETRIES = 3

def enrich_message_with_receipts(gmail_service, msg, message):
    """
    Enrich message with receipt details by searching for matching emails.
    
    Args:
        gmail_service: Gmail API service
        msg: Original message reference
        message: Parsed Message object
        
    Returns:
        Dictionary with enriched data or None if no receipts found
    """
    try:
        # Get full message content for parsing
        full_msg = gmail_service.users().messages().get(
            userId=ME_ID, 
            id=msg[ID], 
            format='full'
        ).execute()
        
        payload = full_msg.get('payload', {})
        
        # Try to extract body text
        from base64 import urlsafe_b64decode
        body_text = ''
        if 'body' in payload and 'data' in payload['body']:
            body_text = urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'replace')
        
        if not body_text:
            return None
        
        # Extract amount and date from the message body
        amount = extract_amount(body_text)
        date = extract_date(body_text)
        
        if not amount or not date:
            logging.debug(f'Could not extract amount ({amount}) or date ({date}) from message {msg[ID]}')
            return None
        
        logging.info(f'Extracted amount {amount} and date {date} from message {msg[ID]}')
        
        # Search for receipt emails with matching date and amount
        searcher = EmailSearcher(gmail_service)
        receipt_messages = searcher.search_receipt_emails(date, amount, days_range=7)
        
        if not receipt_messages:
            logging.debug(f'No receipt emails found for amount {amount} and date {date}')
            return None
        
        # Extract item details from receipt messages
        extractor = ReceiptExtractor()
        all_items = []
        receipt_ids = []
        
        for receipt_msg in receipt_messages:
            receipt_id = receipt_msg.get('id', '')
            # Skip if it's the same message
            if receipt_id == msg[ID]:
                continue
                
            items = extractor.extract_items_from_message(receipt_msg)
            if items:
                all_items.extend(items)
                receipt_ids.append(receipt_id)
                logging.info(f'Extracted {len(items)} items from receipt {receipt_id}')
        
        if all_items:
            return {
                'items': all_items,
                'receipt_ids': receipt_ids
            }
        
        return None
        
    except Exception as e:
        logging.error(f'Error enriching message {msg[ID]}: {e}')
        return None


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

                # Try to enrich message with receipt details
                enriched_data = enrich_message_with_receipts(gmail_service, msg, message)
                
                # Send to RabbitMQ with enriched data
                producer.send_expense_to_rabbitmq(message, enriched_data)
                logging.debug(f'message {msg_id} send to rabbitMQ')

                gmail_service.users().messages().modify(userId=ME_ID,
                                                        id=msg_id,
                                                        body={'removeLabelIds': [LABEL_ID]}
                                                        ).execute()
                logging.debug(f'message {msg_id} label removed')
                
                # Log success with enrichment info
                success_msg = f"{str(message)}: saved successfully"
                if enriched_data and enriched_data.get('items'):
                    success_msg += f" (enriched with {len(enriched_data['items'])} items)"
                producer.send_log_to_rabbitmq('INFO', success_msg)

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
