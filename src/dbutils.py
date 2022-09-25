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

    def insert_transaction(self, message, category_id):
        cursor = self.connection.cursor()
        query = (
                "insert into transaction (transaction_date, title, payee, amount, category_id) " +
                "values (STR_TO_DATE(%s, '" + const.SHORT_F + "'), %s, %s, %s, %s);")
        cursor.execute(query, (message.get_date(), message.get_title(), message.get_who(),
                               message.get_amount(to_string=False), category_id))
        self.connection.commit()
        cursor.close()

    def find_category(self, category_name):
        cursor = self.connection.cursor()
        query = ("select id from category where name = %s")
        cursor.execute(query, (category_name,))
        category = cursor.fetchone()
        category_id = None
        if category is not None:
            category_id = category[0]
        return category_id

    def close_connection(self):
        self.connection.close()
