# Classes and functions to manage the expense Bot

import sqlite3
import time
import uuid
import pandas as pd

class DBHelper:
    def __init__(self, dbname='/var/www/expenseBot/expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), date_expense date, reason text, status text, wbs text, type text, receipt varchar, user varchar)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, iq_username varchar, iq_password varchar, status varchar, email varchar, date_created date, wbs varchar, currency text)'''
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
        Output: list of tuples, one tuple per pending expense'''

        data = (status, activeUser)
        c = self.conn.cursor()
        c.execute('''SELECT amount, date_expense, reason, wbs, type, receipt, uid FROM items WHERE status=? AND user=?''', data)

        return c.fetchall()

    def extract_all(self, activeUser):
        '''Extracts all expenses from a specific user. 
        Input: telegram handle
        Output: saved csv file in a dedicated user folder''' 

        query = 'SELECT * FROM items WHERE user="' + activeUser + '";'
        rawResult = pd.read_sql_query(query, self.conn)

        #Save csv export under a temporary name
        path = '/var/www/expenseBot/exports/' + activeUser + '/'
        filename = path + 'export.csv'
        rawResult.to_csv(filename)

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

    def add_user(self, telegram_username, iq_username, iq_password, email, wbs, ccy):
        '''Adds a user to the users table.
        Input:  telegram username, iq_username, iq_password, user email, wbs, base currency
        Output: new entry in the users table. By default, the user is set to "active"'''

        data = (telegram_username, iq_username, iq_password, 'active', email, time.strftime('%d-%m-%Y'), wbs, ccy)
        stmt = '''INSERT INTO users VALUES (?,?,?,?,?,?,?,?)'''
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

    def update_user(self, telegram_username, iq_username, iq_password, email, wbs, ccy):
        """
        Updates the user data.
        """
        data = (iq_username, iq_password, email, wbs, ccy, telegram_username)
        stmt = '''UPDATE users SET iq_username=?, iq_password=?, email=?, wbs=?, currency=? WHERE telegram_username=?''' 
        self.conn.execute(stmt, data)
        self.conn.commit()

    def update_iq_creds(self, telegram_username, iq_username, iq_password):
        '''Updates only the IQ credentials for a telegram user'''

        data = (iq_username, iq_password, telegram_username)
        stmt = '''UPDATE users SET iq_username=?, iq_password=? WHERE telegram_username=?'''
        
        self.conn.execute(stmt, data)
        self.conn.commit()

    def get_users_by_status(self, status):
        data = (status,)
        c = self.conn.cursor()
        c.execute('''SELECT telegram_username, iq_username, iq_password FROM users WHERE status = ?''', data)

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


################# WBS table helpers    ##############################################
### wbs status can take 3 values: active, inactive, primary. Primary gets called by default

    def get_wbs(self, activeUser):
        """
        Get the primary wbs for a specific telegram user
        Input: telegram handle
        Output: wbs as a string object
        """

        try:
            data = (activeUser,)
            stmt = '''SELECT wbs FROM wbs WHERE telegram_username = ? AND status="primary"'''
            c = self.conn.cursor()
            c.execute(stmt, data)
            result = c.fetchone()       #result is a tuple

        except Exception as e:
            logging.error('Could not retrive wbs from database: %s',e)

        return result[0]

    def update_wbs(self, activeUser, wbs, status):
        """
        Updates the status of a wbs used by the activeUser
        Input: active user telegram handle, wbs number, new status
        Output: None
        """

        #DO NOT forget to also change the status of the former primary wbs to "active"
        data = (wbs, status, activeUser)
        stmt = '''UPDATE wbs SET wbs = ?, status=? WHERE telegram_username = ?'''
        self.conn.execute(stmt, data)
        self.conn.commit()

    def add_wbs(self, activeUser, wbs, status):
        """
        Adds a new default wbs to the wbs table for the active user
        """

        today = time.strftime('%d-%m-%Y')
        data = (wbs, activeUser, today, status)
        stmt = '''INSERT INTO wbs (wbs, telegram_username, date_creation, status)
        VALUES (?, ?, ?, ?)'''
        self.conn.execute(stmt, data)
        self.conn.commit()

    def get_active_wbs(self, activeUser):
        """
        Gets all active wbs for the telegram user
        """
        data = (activeUser,)
        stmt = '''SELECT wbs from wbs WHERE telegram_username = ? AND status="active"'''
        c = self.conn.cursor()
        c.execute(stmt, data)
        query_result = c.fetchall()

        #Creating a list to return only the wbs strings, without the tuples
        result = []
        for wbs in query_result:
            result.append(wbs[0])
        
        return result           # Returns a list of tuples. One tuple per wbs?
    
    def update_last_used(self, wbs, activeUser):
        """
        Update the date of the last use of the given wbs for a user
        """
        today = time.strftime('%d-%m-%Y')
        data = (today, wbs, activeUser)
        stmt = '''UPDATE wbs SET date_last_used = ? WHERE wbs = ? AND telegram_username = ?'''
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



class Expense:
    def __init__(self, amount=None, wbs=None, receipt=None, reason=None, typex='17819687102', user=None):
        self.uid = str(uuid.uuid4())
        self.amount = amount
        self.date = time.strftime("%d-%-m-%Y")
        self.wbs = wbs
        self.receipt = receipt
        self.reason = reason
        self.typex = typex
        self.status = 'pending'
        self.user = user

    def to_tuple(self):
        '''Converts the data in the expense class into a tuple.
        Input: expense class with all data
        Output: a data tuple, ready for injection in the db'''

        data_tuple = (self.uid, self.amount, self.date, self.reason, self.status, self.wbs, self.typex, self.receipt, self.user)
        return data_tuple


