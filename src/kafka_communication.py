import json
from datetime import datetime

from kafka import KafkaProducer


class KafkaCommunication:
    producer = None

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9093'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer.close()

    def send_expense_to_kafka(self, message):
        self.producer.send('expense',
                           {
                               'title': message.get_title(),
                               'payee': message.get_who(),
                               'amount': message.get_amount(False),
                               'transactionDate': message.get_date().strftime('%Y-%m-%d %H:%M:%S'),
                               'sendDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                           })

    def send_log_to_kafka(self, level, message):
        self.producer.send('log',
                           {
                               'level': level,
                               'message': message,
                               'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                           })
