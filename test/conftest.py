#standard imports
import sys
import pytest

#Add expenseBot folder to sys.path to be able to import the app's modules
sys.path.append('/var/www/expenseBot/')

#Class import
from botClasses.classes import *

@pytest.fixture
def setup_database():
    """ Fixture to set up the in-memory database with test data """

    import sqlite3
    import csv

    db = DBHelper()
    db.conn = sqlite3.connect(':memory:')
    cursor = db.conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), currency varchar, date_expense date, reason text, status text, typex text, receipt varchar, user varchar)''')

    l = []
    with open('/var/www/expenseBot/test/testData.csv') as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            l.append(row)
        sample_data = tuple(l)
    cursor.executemany('INSERT INTO items VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_data)
    return db.conn

@pytest.fixture
def setup_user_database():
    """Fixture to create a user database"""

    import sqlite3
    db = DBHelper()
    db.conn = sqlite3.connect(':memory:')
    cursor = db.conn.cursor()

    stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, status varchar, email varchar, date_created date, currency text)'''
    db.conn.execute(stmt)
    db.conn.commit()

    stmt = '''INSERT INTO users VALUES(?,?,?,?,?)'''
    data = ('testUser','active','user@gmail.com','01/01/2000','EUR')
    db.conn.execute(stmt, data)

    return db.conn