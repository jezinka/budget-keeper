from datetime import datetime

from peewee import *

from src import dbconfig

db = MySQLDatabase(dbconfig.DB_NAME, user=dbconfig.DB_USER, password=dbconfig.DB_PASSWORD, host=dbconfig.DB_HOST,
                   port=3306)


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    id = DecimalField()
    name = TextField()


class Expense(BaseModel):
    id = DecimalField()
    transaction_date = DateTimeField()
    title = TextField()
    payee = TextField()
    amount = DoubleField()
    category = ForeignKeyField(Category)


class Log(BaseModel):
    id = DecimalField()
    date = DateTimeField(default=datetime.now)
    type = TextField()
    message = TextField()


class FixedCost(BaseModel):
    id = DecimalField()
    name = TextField()
    amount = DoubleField()
    conditions = TextField()

    class Meta:
        table_name = 'fixed_cost'


class FixedCostPayed(BaseModel):
    id = DecimalField()
    pay_date = DateTimeField(default=datetime.now)
    amount = DoubleField()
    fixed_cost = ForeignKeyField(FixedCost)

    class Meta:
        table_name = 'fixed_cost_payed'
