import pytest
import sys

sys.path.append('/var/www/expenseBot/')

from botClasses.reportClass import *

@pytest.fixture
def expenseList():
    #Create a list of expense object, properly filled out
    expenses = []

def test_generate(setup_database):
    report = ExpenseReport('testUser')