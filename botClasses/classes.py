# Classes and functions to manage the expense Bot

import sqlite3
import time

class DBHelper:
    def __init__(self, dbname='/var/www/expenseBot/expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt varchar, user varchar)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, data_tuple):
        stmt = "INSERT INTO items VALUES (?,?,?,?,?,?,?,?)"
        self.conn.execute(stmt, data_tuple)
        self.conn.commit()

    def extract_pending(self, activeUser):
        '''Extracts all expenses with a 'pending' status. Returns a list of data tuple rows.
        Input: an active user (telegram username)
        Output: list of tuples, one tuple per pending expense'''

        status = ("pending", activeUser)
        c = self.conn.cursor()
        c.execute('''SELECT amount, date_expense, reason, wbs, type, receipt FROM items WHERE status=? AND user=?''', status)

        return c.fetchall()

    def updateStatus(self, currentStatus, newStatus, telegram_username):
        '''Modifies the status the expenses that have been logged into IQ Navigator. New status: logged'''

        data = (newStatus, currentStatus, telegram_username)
        c = self.conn.cursor()
        c.execute('''UPDATE items SET status = ? WHERE status = ? AND user = ?''', data)
        self.conn.commit()

class Expense:
    def __init__(self):
        self.amount = None
        self.date = time.strftime("%d-%-m-%Y")
        self.wbs = None
        self.receipt = None
        self.reason = None
        self.type = 'Other expenses'
        self.status = 'pending'
        self.user = None

    def to_tuple(self):
        '''Converts the data in the expense class into a tuple.
        Input: expense class with all data
        Output: a data tuple, ready for injection in the db'''

        data_tuple = (self.amount, self.date, self.reason, self.status, self.wbs, self.type, self.receipt, self.user)
        return data_tuple

#def deductType(expense):
#   '''Deducts the expense type (IQ Navigator categories) based on what has been given to the exp.reason attribute'''
#
#   #We infer the expense type by confronting the value in exp.reason to a list of possible words.
#   #If none matches, the exp.type attribute is set to 'Misc. Expenses'
#
#   types = {'Lodging':['hotel','airbnb','pension','hostel'],
#           'Transportation':['train','taxi','bus','ferry','sbb','eurostar','sncf','thalys'],
#   'Airfare':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
#   'Rental Car':['avis','entreprise','rental car','alamo'],
#   'Business Meals':['restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','brekfast'],
#   'Misc. Travel':['highway','public','gas','petrol']}
#
#   #The magic loop, where the deduction happens
#   for accType, typeList in types.items():
#       for elt in typeList:
#           if elt in expense.reason.lower():
#               expense.type = accType
#
#   return expense

class userDB:
    def __init__(self, dbname='/var/www/expenseBot/users.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, iq_username varchar, iq_password varchar, status varchar, email varchar, date_created date)'''
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, telegram_username, iq_username, iq_password, email):
        '''Adds a user to the users table.
        Input:  telegram username, iq_username, iq_password, user email
        Output: new entry in the users table. By default, the user is set to "active"'''

        data = (telegram_username, iq_username, iq_password, 'active', email, time.strftime('%d-%m-%Y'))
        stmt = '''INSERT INTO users VALUES (?,?,?,?,?,?)'''
        self.conn.execute(stmt, data)
        self.conn.commit()

    def get_users_by_status(self, status):
        data = (status,)
        c = self.conn.cursor()
        c.execute('''SELECT telegram_username, iq_username, iq_password FROM users WHERE status = ?''', data)

        return c.fetchall()

    def get_iqn_credentials(self, activeUserTelegram):
        '''Gets a username and password from the users database.
        Input: telegram username
        Output: tuple containing username and password'''

        data = (activeUserTelegram,)
        stmt = '''SELECT iq_username, iq_password FROM users WHERE telegram_username = ?'''
        c = self.conn.cursor()
        c.execute(stmt, data)

        return c.fetchone()

    def del_user_by_iq_username(self,iq_username):
        stmt = '''DELETE FROM users WHERE iq_username = ?'''
        data = (iq_username,)
        self.conn.execute(stmt, data)
        self.conn.commit()
