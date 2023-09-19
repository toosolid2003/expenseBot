# Classes and functions to manage the expense Bot

import sqlite3
import time
import pandas as pd
from logger.logger import logger
from uuid import uuid4
from botFunctions.botData.parserData import *
import re

class DBHelper:
    def __init__(self, dbname='/var/www/expenseBot/expenses.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (uid varchar, amount float (2), currency varchar, date_expense date, reason varchar, status varchar, typex varchar, receipt varchar, user varchar)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = '''CREATE TABLE IF NOT EXISTS users (telegram_username varchar, status varchar, email varchar, date_created date, currency text)'''
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = '''CREATE TABLE IF NOT EXISTS analytics (time datetime, user varchar, action varchar, value varchar)'''
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
        c.execute('''SELECT amount, currency, date_expense, reason, typex, receipt, uid FROM items WHERE status=? AND user=?''', data)

        return c.fetchall()
    
    def extract_exp_date(self, activeUser, date_exp):
        '''Extract all expenses from the specified date'''

        c = self.conn.cursor()
        data = (date_exp, activeUser)
        c.execute('''SELECT reason, amount, currency, date_expense, typex, receipt FROM items WHERE date_expense >=? AND user=?''', data)
        expenseTuple = c.fetchall()
        
        return list(expenseTuple)


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

    def add_user(self, telegram_username, email, ccy):
        '''Adds a user to the users table.
        Input:  telegram username, user email, date of creation, base currency
        Output: new entry in the users table. By default, the user is set to "active"'''

        data = (telegram_username, 'beta', email, time.strftime('%d-%m-%Y'), ccy)
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

####################### Expense Class ######################################
# This class is not currently being used. Saved for a later code refactoring

class Expense:
    def __init__(self):
        self.date_created = time.strftime("%Y-%m-%d")
        self.uid = str(uuid4())
        self.split = None 
        self.status = 'pending'
        self.amount = None
        self.reason = None
        self.typex = 'various'
        self.ccy = None
        self.user = None
        self.receipt = None
        self.complete = False
    
    def split(self, textInput):
        '''
        Split the text input into a list, using 3 delimeters:"," OR " " OR "-"
        Input: text string
        Output: list stored in the expense object
        '''
        self.split = re.split(r',| |-', textInput)
    
    def getCcy(self):
        '''
        Returns the currency if specified in the user input:
        Input: split string from user input
        Output: trigram (string) of the currency or None, if no currency spcified, store
        in the expense object.
        '''
        #We compare two sets to find the intersection. If the user has specified a currency
        #in his input, and if this currency is managed, then we find it.
        res = set(self.split) & set(managedCcy)
        
        #If the currency has been found, we store it in the expense object. If not, 
        #leave the object as is.
        if len(res) > 0:
            self.ccy = list(res)[0]
    
    def getType(self):
        '''
        Deduct the type of expense from a word list that is managed separately.
        Input: split string from user input.
        Output: expense type as string and store it in the expense object. If no type
        found, the attribute stays on its default value, 'various'.
        '''

           #The magic loop, where the deduction happens
        for accType, typeList in types.items():
            for elt in typeList:
                if elt in self.split:
                    self.typex = accType
     
    def getAmount(self):
        for elt in self.split:
            try:
                self.amount = float(elt)
            except:
                pass
    
    def addReason(self):
        '''
        Adds a reason for the expense, based on the text inputted by the user.
        Input: self.split, string
        Output: self.reason completed
        '''
        self.reason = " ".join(self.split)

    def checkComplete(self):
        #Check if all attributes are filled
        if any(elt == None for elt in self.__dict__.values()):
            self.complete = False
        else:
            self.complete = True

    def to_tuple(self):
        newTuple = (self.uid,
                self.amount,
                self.ccy,
                self.date_created,
                self.reason,
                self.status,
                self.typex,
                self.receipt,
                self.user,
                )
        return newTuple

    def assign(self, dico):
        """Takes the input from dictionnary, put them into the expense object as attributes"""

        for elt, value in dico.items():
        #Checks if the key in the provided dictionnary actually exists in the expense object
            if elt in self.__dict__.keys():
                self.__setattr__(elt, value)

    def add_to_db(self, dbname):
        """Adds the completed expense to the items table in the db"""

        if self.complete == False:
            return print(f'Expense is missing required data')
        else:
            conn = sqlite3.connect(dbname, check_same_thread=False)
            data = self.to_tuple()
            conn.execute('''INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?)''', data)
            conn.commit()
            return print('Expense correctly saved in the db')
