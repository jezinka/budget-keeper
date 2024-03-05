import json
from datetime import datetime

from kafka import KafkaProducer


class KafkaCommunication:
    producer = None

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9093'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )

    def send_expense_to_kafka(self, message):
        self.producer.send('expense',
                           {
                               'title': message.get_title(),
                               'payee': message.get_who(),
                               'amount': message.get_amount(True),
                               'transactionDate': message.get_date(),
                               'sendDate': datetime.now().isoformat()
                           })

    def send_log_to_kafka(self, level, message):
        self.producer.send('log',
                           {
                               'level': level,
                               'message': message,
                               'date': datetime.now().isoformat()
                           })
