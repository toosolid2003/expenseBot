# Standard imports 
import pytest
import sys

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

    insertData = ('a6d0865f-e06b-4c26-ac3a-4fb6014db3dc',10.12,'EUR','01/08/2021','hotel acapulco','logged','accomodation','/file/receipt.jpg','thedropper')
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
    assert result[4] == 'Car rental'

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
    assert result[5] == 'updated'

def test_extract_expenses(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    result = db.extract_expenses('testUser','logged')
    assert result is not None
    assert result[0][0] == 1000.01  #The uid is not collected by the function, this is why we have amount first

#@pytest.mark.skip(reason='Dont want to save a file on the server')

def test_update_multiple_statuses(setup_database):
    db = DBHelper()
    db.conn = setup_database
    c = db.conn.cursor()

    db.updateStatus('logged','updated','testUser')

    result = db.extract_expenses('testUser','updated')
    assert len(result) == 15

def test_extract_by_date(setup_database):
    db = DBHelper()
    ##Fix the setup db first, testData.csv



########################################## Databse User Tests ####################################

def test_get_user(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    result = db.get_user_email('testUser')
    assert result == 'user@gmail.com'


def test_add_user(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    db.add_user('testUsername','test@expensebot.net','eur')
    assert db.get_user_email('testUsername') == 'test@expensebot.net'

def test_check_existing_user(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    assert db.checkExistingUser('testUser') == True

def test_get_user_by_status(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    result = db.get_users_by_status('active')
    assert result[0] == ('testUser','user@gmail.com','01/01/2000')


def test_get_ccy(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    result = db.get_ccy('testUser')
    assert result == 'EUR'

def test_get_user_email(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()   

    result = db.get_user_email('testUser')
    assert result == 'user@gmail.com'

def test_update_user_email(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    db.update_user_email('testUser','tg@gmail.com')

    assert db.get_user_email('testUser') == 'tg@gmail.com'

##############  Expense Classes Tests  ######################

@pytest.fixture(scope='session')
def expenseFixture():
    from uuid import uuid4

    exp = Expense()
    exp.amount = 1000.00
    exp.ccy = 'EUR'
    exp.date_created = '01-01-2000'
    exp.reason = 'hotel Marmara'
    exp.typex = 'accomodation'
    exp.uid = str(uuid4())
    exp.user = 'thib'
    exp.receipt = '/tmp'
    exp.split = ['1000','eur','hotel','Marmara']

    return exp

def test_checkComplete(expenseFixture):
    newExpense = Expense()

    newExpense.checkComplete()
    assert newExpense.complete == False

    expenseFixture.checkComplete()
    assert expenseFixture.complete == True

def test_to_tuple(expenseFixture):

    #We check that we generate a tuple with the right number of data point before injection
    assert len(expenseFixture.to_tuple()) == 9

def test_add_to_db(expenseFixture):

    conn = sqlite3.connect('testItems.sqlite')
    c = conn.cursor()
    data = expenseFixture.to_tuple()
    c.execute('''INSERT INTO items VALUES (?,?,?,?,?,?,?,?,?)''', data)

    data = (expenseFixture.uid,)
    c.execute('''SELECT * FROM items WHERE uid=?''', data)
    result = c.fetchall()

    assert result[0][0] == expenseFixture.uid

def test_assign(expenseFixture):
    testDic = {
        'amount': 122.09,
        'reason': 'restaurant labatte',
        'typex': 'food & beverage',
        'ccy': 'EUR',
        'falseAttr': 'should not be there',
    }

    expenseFixture.assign(testDic)

    assert expenseFixture.amount == 122.09
    assert expenseFixture.reason == 'restaurant labatte'
    assert expenseFixture.typex == 'food & beverage'
    assert expenseFixture.ccy == 'EUR'

    #Also checking if the 'assign' method does not add unwanted attributes to the instance
    with pytest.raises(AttributeError):
        expenseFixture.falseAttr 
        