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
    ]
)
def test_integration_simple(userInput, amnt, typex):
    #userInput = '165.87, hotel la mer bleue'

    dico = {}
    dico = parseText(userInput, 'testUser')
    dico['receipt'] = '/test'
    dico['user'] = 'testUser'
    dico['currency'] = 'EUR'
    uid = injectData(dico)

    #Getting the newly injected item
    db = DBHelper()
    result = db.get_item(uid)
    
    #Assert part
    assert pytest.approx(result[1] == amnt)
    assert result[6] == typex
    
    #Deleting new entry from PRODUCTION database
    db.del_item(uid)

