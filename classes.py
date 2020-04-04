# Ensemble de fonctions pour gerer la BD de mes expenses.

import sqlite3
import time

class DBHelper:
    def __init__(self, dbname='expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt longblob)"
        self.conn.execute(stmt)
        self.conn.commit

    def add_item(self, data_tuple):
        stmt = "INSERT INTO items VALUES (?,?,?,?,?,?,?)"
        self.conn.execute(stmt, data_tuple)
        self.conn.commit()

    def extract_pending(self):
        '''Extracts all expenses with a 'pending' status. Returns a list of data tuple rows'''
        status = ("pending",)
        c = self.conn.cursor()
        c.execute('''SELECT * FROM items WHERE status=?''', status)

        return c.fetchall()

class Expense:
    def __init__(self):
        self.amount = None
        self.date = time.strftime("%Y-%m-%d")
        self.wbs = None
        self.receipt = None
        self.reason = None
        self.type = None
        self.status = 'pending'

    def to_tuple(self):
        '''Converts the data in the expense class into a tuple.
        Input: expense class with all data
        Output: a data tuple, ready for injection in the db'''

        data_tuple = (self.amount, self.date, self.reason, self.status, self.wbs, self.type, self.receipt)
        return data_tuple

    def deductType(self):
        '''Deducts the expense type (IQ Navigator categories) based on what has been given to the exp.reason attribute'''

        #We infer the expense type by confronting the value in exp.reason to a list of possible words.
        #If none matches, the exp.type attribute is set to 'Misc. Expenses'

        types = {'Lodging':['hotel','airbnb','pension','hostel'], 
                'Transportation':['train','taxi','bus','ferry','sbb','eurostar','sncf','thalys'],
        'Airfare':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
        'Rental Car':['avis','entreprise','rental car','alamo'],
        'Business Meals':['restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','brekfast'],
        'Misc. Travel':['highway','public','gas','petrol']}

        #The magic loop, where the deduction happens
        for accType, typeList in types.items():
            for elt in typeList:
                if elt in exp.reason.lower():
                    exp.type = accType
                else:
                    exp.type = 'Misc. Expenses'
        if exp.type == None:
            exp.type = 'Misc. Expenses'
