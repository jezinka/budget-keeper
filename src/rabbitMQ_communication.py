import json
from datetime import datetime

import pika

from const import RABBITMQ_USER, RABBITMQ_PASSWORD


class RabbitMQCommunication:
    connection = None
    channel = None

    def __init__(self):
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=credentials))
        self.channel = self.connection.channel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def send_expense_to_rabbitmq(self, message):
        self.channel.basic_publish(exchange='',
                                   routing_key='expense',
                                   body=json.dumps({
                                       'title': message.get_title(),
                                       'payee': message.get_who(),
                                       'amount': message.get_amount(False),
                                       'transactionDate': message.get_date().strftime('%Y-%m-%d %H:%M:%S'),
                                       'sendDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                   }))

    def send_log_to_rabbitmq(self, level, message):
        self.channel.basic_publish(exchange='',
                                   routing_key='log',
                                   body=json.dumps({
                                       'level': level,
                                       'message': message,
                                       'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                   }))
