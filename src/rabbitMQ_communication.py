import json
from datetime import datetime

import pika

from const import RABBITMQ_USER, RABBITMQ_PASSWORD


class RabbitMQCommunication:

    def __init__(self):
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=credentials))
        self.channel = self.connection.channel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def send_expense_to_rabbitmq(self, message, enriched_data=None):
        """
        Send expense message to RabbitMQ.
        
        Args:
            message: Message object with transaction data
            enriched_data: Optional dict with enriched data like {'items': [...], 'receipt_ids': [...]}
        """
        body_dict = {
            'title': message.get_title(),
            'payee': message.get_who(),
            'amount': message.get_amount(False),
            'transactionDate': message.get_date().strftime('%Y-%m-%d %H:%M:%S'),
            'sendDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add enriched data if available
        if enriched_data:
            if 'items' in enriched_data and enriched_data['items']:
                body_dict['items'] = enriched_data['items']
            if 'receipt_ids' in enriched_data and enriched_data['receipt_ids']:
                body_dict['receiptIds'] = enriched_data['receipt_ids']
        
        body = json.dumps(body_dict)
        self.channel.basic_publish(exchange='', routing_key='expense', body=body)

    def send_log_to_rabbitmq(self, level, message):
        body = json.dumps({
            'level': level,
            'message': message,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.channel.basic_publish(exchange='', routing_key='log', body=body)
