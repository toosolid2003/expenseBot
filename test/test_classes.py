# Standard imports 
import pytest
import sys
from pandas import Timestamp

#Add expenseBot folder to sys.path to be able to import the app's modules
sys.path.append('/var/www/expenseBot/')

#Class import
from botClasses.classes import *


def test_connection(setup_database):
    # Test to make sure that there are 15 items in the database

    db = DBHelper()
    db.conn = setup_database
    assert len(list(db.conn.execute('SELECT * FROM items'))) == 15

def test_add_item(setup_database):
    #Test to check id adding a new entry works
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    insertData = ('a6d0865f-e06b-4c26-ac3a-4fb6014db3dc',10.12,'01/08/2021','hotel acapulco','logged','wbs','accomodation','/file/receipt.jpg','thedropper')
    db.add_item(insertData)
    c.execute("SELECT * FROM items WHERE uid='a6d0865f-e06b-4c26-ac3a-4fb6014db3dc'")
    result = c.fetchone()
    assert result is not None
    assert result[0] == 'a6d0865f-e06b-4c26-ac3a-4fb6014db3dc'

def test_get_item(setup_database):
    #Test for the get_item method of the DBHelper class
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    result = db.get_item('test15')
    assert result is not None
    assert result[3] == 'Car rental'

def test_del_item(setup_database):
    #Test for the del_item method of the DBHelper class
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    db.del_item('test15')
    assert db.get_item('test15') is None

def test_update_status(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    db.update_item_status('test01','updated')
    result = db.get_item('test01')
    assert result[4] == 'updated'

def test_extract_expenses(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    result = db.extract_expenses('testUser','logged')
    assert result is not None
    assert result[0][0] == 1000.01  #The uid is not collected by the function, this is why we have amount first

def test_extract_all(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    timestamp = pd.Timestamp.now()
    timestamp = str(timestamp)
    expectedPath = '/var/www/expenseBot/exports/testUser/'+'testUser_export_' + timestamp[:10] +'.csv'
    assert db.extract_all('testUser') == expectedPath 

def test_update_multiple_statuses(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    db.updateStatus('logged','updated','testUser')

    result = db.extract_expenses('testUser','updated')
    assert len(result) == 15