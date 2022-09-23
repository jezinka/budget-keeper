import time

import mysql.connector as mariadb

import const


class DbUtils:
    connection = None

    def __init__(self):
        time.sleep(15)
        self.connection = mariadb.connect(user=const.DB_USER, password=const.DB_PASSWORD,
                                          host='maria_db',
                                          database='budget')

    def insert_transaction(self, message):
        cursor = self.connection.cursor()
        query = (
                "insert into transaction (transaction_date, title, payee, amount, category) " +
                "values (STR_TO_DATE(%s, '" + const.SHORT_F + "'), %s, %s, %s, %s);")
        cursor.execute(query, (message.get_date(), message.get_title(), message.get_who(),
                               message.get_amount(to_string=False), message.get_category()))
        self.connection.commit()
        cursor.close()

    def close_connection(self):
        self.connection.close()