#standard imports
import sys
import sqlite3
import csv
import pytest

#Add expenseBot folder to sys.path to be able to import the app's modules
sys.path.append('/var/www/expenseBot/')

#Class import
from botClasses.classes import *

@pytest.fixture
def setup_database():
    """ Fixture to set up the in-memory database with test data """

    db = DBHelper()
    db.conn = sqlite3.connect(':memory:')
    cursor = db.conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt varchar, user varchar)''')

    l = []
    with open('/var/www/expenseBot/test/testData.csv') as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            l.append(row)
        sample_data = tuple(l)
    cursor.executemany('INSERT INTO items VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', sample_data)
    yield db.conn

