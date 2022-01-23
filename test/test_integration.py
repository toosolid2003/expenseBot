# Standard imports 
import pytest
import sys

#Add expenseBot folder to sys.path to be able to import the app's modules
sys.path.append('/var/www/expenseBot/')

#Class import
from botClasses.classes import *
from botFunctions.botLogic import *

@pytest.mark.parametrize(
    "userInput, amnt, typex",
    [
        ('160 chf, restaurant', 150.00, 'food & beverage'),
        ('100, car rental', 100.00,'car rental'),
        ('200 eur, hotel novotel', 200.00, 'accomodation'),
    ]
)
def test_integration_simple(userInput, amnt, typex):
    #userInput = '165.87, hotel la mer bleue'
#    dico = {}
#    dico = parseText(userInput, 'testUser')
#    dico['receipt'] = '/test'
#    dico['user'] = 'testUser'
#    dico['currency'] = 'EUR'
#    uid = injectData(dico)
    exp = Expense()
    
    dico = {}
    dico = parseText(userInput, 'testUser')
    
    exp.receipt = '/var/test'
    exp.user = 'testUser'
    exp.ccy = 'EUR'

    exp.assign(dico)
    exp.checkComplete()
    exp.add_to_db('expenses.sqlite')

    #Getting the newly injected item
    db = DBHelper()
    result = db.get_item(exp.uid)
    
    #Assert part
    assert pytest.approx(result[1] == amnt)
    assert result[6] == typex
    
    #Deleting new entry from PRODUCTION database
    db.del_item(exp.uid)

