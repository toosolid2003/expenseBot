import sys
import pytest

sys.path.append('/var/www/expenseBot/')

from botFunctions.botLogic import *

@pytest.mark.parametrize("inputs, expected",
[
    ({
        'amount':1.0,
        'reason':'restaurant',
        'typex':'food & beverage',
        'receipt':'/tmp',
        'user':'testUser',
    },True),
    ({
        'amount':1.0,
        'reason':'restaurant',
        'typex':'food & beverage',
        'user':'testUser',
    }, False),
    ({
        'amount':1.0,
        'reason':'hotel acapulco major',
        'typex':'accomodation',
        'receipt':'/var/tmp/',
        'user':'testUser',
        'wbs':'XBG501',
    }, True)  
]
)
def test_check_completion(inputs, expected):
    assert checkCompletion(inputs) == expected

@pytest.mark.parametrize(
    "inputs, expected",
    [
        ("12, hotel",{'amount':12.00,'reason':'hotel','typex':'accomodation'}),
        ("14, restau acapulco",{'amount':14.00,'reason':'restau acapulco','typex':'food & beverage'}),
        ("12 chf, car rental avis",{'amount':11.20,'reason':'car rental avis','typex':'car rental'}),

    ]
)
def test_parseText(setup_database, inputs, expected):
    assert pytest.approx(parseText(inputs,'testUser') == expected)

def test_get_ccy(setup_user_database):
    db = DBHelper()
    db.conn = setup_user_database
    c = db.conn.cursor()

    result = db.get_ccy('testUser')
    assert result == 'EUR'

@pytest.mark.parametrize(
    "input, result",
    [
    (['10','eur','hotel','acapulco'], 10.00),
    (['10.01','eur','hotel','acapulco'], 10.01),
    (['10.012','eur','hotel','acapulco'], 10.01),
    ])
def test_get_amount(input, result):
    assert getAmount(input) == result

def test_get_type():
    input = ['10','eur','hotel','acapulco']
    assert getType(input) == 'accomodation'

def test_exportFile(setup_database):
    from datetime import datetime
    date_exp = datetime(2021,5,5)
    filename = exportFile('testUser', date_exp)
    expectedFilename = '/var/www/expenseBot/exports/testUser/export_' + datetime.today().strftime('%Y_%m_%d') + '.csv'
    assert filename == expectedFilename