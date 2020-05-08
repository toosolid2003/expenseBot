# Classes and functions to manage the expense Bot

import sqlite3
import time
import uuid

class DBHelper:
    def __init__(self, dbname='/var/www/expenseBot/expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt varchar, user varchar)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, data_tuple):
        stmt = "INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?)"
        self.conn.execute(stmt, data_tuple)
        self.conn.commit()

    def get_item(self, uid):
        """
        Gets a single expense with its unique identifier
        """

        data = (uid,)
        stmt = '''SELECT * FROM items WHERE uid=?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        result = c.fetchone()

        return result

    def del_item(self, uid):
        """
        Deletes an expense with a uid.
        """
        
        data = (uid,)
        stmt = '''DELETE FROM items WHERE uid=?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        self.conn.commit()

    def update_item_status(self, uid, status):
        """Updates a field of an expense"""

        data = (status, uid)
        stmt = '''UPDATE items SET status = ? WHERE uid = ?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        self.conn.commit()

    def extract_expenses(self, activeUser, status):
        '''Extracts all expenses with a specific status. Returns a list of data tuple rows.
        Input: an active user (telegram username) and a status.
        Output: list of tuples, one tuple per pending expense'''

        data = (status, activeUser)
        c = self.conn.cursor()
        c.execute('''SELECT amount, date_expense, reason, wbs, type, receipt, uid FROM items WHERE status=? AND user=?''', data)

        return c.fetchall()

    def updateStatus(self, currentStatus, newStatus, telegram_username):
        '''
        Updates the status of all expenses matching a current status, per user.
        Returns nothing. Just updated the db.
        '''

        data = (newStatus, currentStatus, telegram_username)
        c = self.conn.cursor()
        c.execute('''UPDATE items SET status = ? WHERE status = ? AND user = ?''', data)
        self.conn.commit()

class Expense:
    def __init__(self, amount=None, wbs=None, receipt=None, reason=None, user=None):
        self.uid = str(uuid.uuid4())
        self.amount = amount
        self.date = time.strftime("%d-%-m-%Y")
        self.wbs = wbs
        self.receipt = receipt
        self.reason = reason
        self.type = '17819687102'
        self.status = 'pending'
        self.user = user

    def to_tuple(self):
        '''Converts the data in the expense class into a tuple.
        Input: expense class with all data
        Output: a data tuple, ready for injection in the db'''

        data_tuple = (self.uid, self.amount, self.date, self.reason, self.status, self.wbs, self.type, self.receipt, self.user)
        return data_tuple

class userDB:
    def __init__(self, dbname='/var/www/expenseBot/users.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, iq_username varchar, iq_password varchar, status varchar, email varchar, date_created date, wbs varchar, currency text)'''
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, telegram_username, iq_username, iq_password, email, wbs, ccy):
        '''Adds a user to the users table.
        Input:  telegram username, iq_username, iq_password, user email, wbs, base currency
        Output: new entry in the users table. By default, the user is set to "active"'''

        data = (telegram_username, iq_username, iq_password, 'active', email, time.strftime('%d-%m-%Y'), wbs, ccy)
        stmt = '''INSERT INTO users VALUES (?,?,?,?,?,?,?,?)'''
        self.conn.execute(stmt, data)
        self.conn.commit()

    def get_users_by_status(self, status):
        data = (status,)
        c = self.conn.cursor()
        c.execute('''SELECT telegram_username, iq_username, iq_password FROM users WHERE status = ?''', data)

        return c.fetchall()

    def get_wbs(self, activeUser):
        """
        Get the active wbs for a specific telegram user
        Input: telegram handle
        Output: wbs as a string object
        """

        try:
            data = (activeUser,)
            stmt = '''SELECT wbs FROM users WHERE telegram_username = ?'''
            c = self.conn.cursor()
            c.execute(stmt, data)
            result = c.fetchone()       #result is a tuple

        except Exception as e:
            logging.error('Could not retrive wbs from database: %s',e)

        return result[0]

    def update_wbs(self, activeUser, wbs):
        """
        Add or changes the current wbs used by the activeUser
        Input: active user telegram handle, wbs number
        Output: None
        """

        data = (wbs, activeUser)
        stmt = '''UPDATE users SET wbs = ? WHERE telegram_username = ?'''
        self.conn.execute(stmt, data)
        self.conn.commit()


    def get_ccy(self, activeUser):
        """
        Gets the preferred currency of the activeUser.

        Input: telegram handle of the user
        Output: currency trigram
        """
        
        data = (activeUser,)
        stmt = '''SELECT currency FROM users WHERE telegram_username = ?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        result = c.fetchone()

        return result[0]

    def get_credentials(self, telegram_username):

        stmt = '''SELECT iq_username, iq_password FROM users WHERE telegram_username=?'''
        data = (telegram_username,)
        c = self.conn.cursor()
        c.execute(stmt, data)
        result = c.fetchone()

        return result

    def del_user_by_iq_username(self,iq_username):
        stmt = '''DELETE FROM users WHERE iq_username = ?'''
        data = (iq_username,)
        self.conn.execute(stmt, data)
        self.conn.commit()
