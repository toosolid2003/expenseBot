# Classes and functions to manage the expense Bot

import sqlite3
import time
import pandas as pd
from logger.logger import logger


class DBHelper:
    def __init__(self, dbname='/var/www/expenseBot/expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt varchar, user varchar)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, status varchar, email varchar, date_created date, currency text)'''
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

    def update_item_wbs(self, wbs, uid):
        """Reallocate an expense to another wbs"""

        data = (wbs, uid)
        stmt = '''UPDATE items SET wbs = ? WHERE uid = ?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        self.conn.commit()

    def extract_expenses(self, activeUser, status):
        '''Extracts all expenses with a specific status. Returns a list of data tuple rows.
        Input: an active user (telegram username) and a status.
        Output: list of tuples, one tuple per expense'''

        data = (status, activeUser)
        c = self.conn.cursor()
        c.execute('''SELECT amount, date_expense, reason, wbs, type, receipt, uid FROM items WHERE status=? AND user=?''', data)

        return c.fetchall()

    def extract_all(self, activeUser, path='/var/www/expenseBot/exports/'):
        '''Extracts all expenses from a specific user. 
        Input: telegram handle
        Output: absolute filepath to the exported csv file with all expenses for activeUser'''

        query = 'SELECT date_expense, amount, reason, type FROM items WHERE user="' + activeUser + '";'
        rawResult = pd.read_sql_query(query, self.conn)

        #Create a dedicated filename
        timestamp = pd.Timestamp.now()
        timestamp = str(timestamp)
        
        #Only the first 10 characters of the timestamp: the date in dd-mm-yyyy format
        timestamp = timestamp[:10]
        filename = activeUser + '_export_' + timestamp + '.csv'

        #Saving the file in the dedicated user folder
        path +=  activeUser + '/' + filename
        rawResult.to_csv(path)

        return path

    def updateStatus(self, currentStatus, newStatus, telegram_username):
        '''
        Updates the status of all expenses matching a current status, per user.
        Returns nothing. Just updated the db.
        '''

        data = (newStatus, currentStatus, telegram_username)
        c = self.conn.cursor()
        c.execute('''UPDATE items SET status = ? WHERE status = ? AND user = ?''', data)
        self.conn.commit()





################# User Table Helpers #################################

    def add_user(self, telegram_username, status, email, date, ccy):
        '''Adds a user to the users table.
        Input:  telegram username, user email, date of creation, base currency
        Output: new entry in the users table. By default, the user is set to "active"'''

        data = (telegram_username, 'active', email, time.strftime('%d-%m-%Y'), ccy)
        stmt = '''INSERT INTO users VALUES (?,?,?,?,?)'''
        self.conn.execute(stmt, data)
        self.conn.commit()

    def checkExistingUser(self, telegram_username):
        """
        Checks if a user already exists in the database. Takes the telegram handle as input (it's unique).
        Returns:
         - True if the user exists
         - False if she does not.
         """

        data = (telegram_username,)
        stmt = '''SELECT * FROM users WHERE telegram_username=?'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        result = c.fetchone()
        
        if result:
            return True
        else:
            return False

    def get_users_by_status(self, status):
        data = (status,)
        c = self.conn.cursor()
        c.execute('''SELECT telegram_username, email, date_created FROM users WHERE status = ?''', data)

        return c.fetchall()

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

        
    def get_user_email(self, telegram_username):
        stmt = '''SELECT email FROM users WHERE telegram_username=?'''
        data = (telegram_username,)
        c = self.conn.cursor()
        c.execute(stmt, data)
        result = c.fetchone()

        return result[0]

    def update_user_email(self, telegram_username, mel):
        """Changes the email address for the user."""
        
        stmt = '''UPDATE users SET email=? WHERE telegram_username=?'''
        data = (mel, telegram_username)
        self.conn.execute(stmt, data)
        self.conn.commit()

################### Analytics helpers #####################################

    def add_datapoint(self, user, action, value):
        """
        Records a new data point for an action performed by a user
        """

        data = (time.ctime(),user, action, value)
        stmt = '''INSERT INTO analytics (time, user, action, value) VALUES (?,?,?,?)'''
        self.conn.execute(stmt, data)
        self.conn.commit()