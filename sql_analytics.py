# coding: utf-8
from sqlalchemy import create_engine
engine = create_engine('sqlite:////var/www/expenseBot/expenses.sqlite')
res = engine.execute('select * from analytics;').fetchall()
