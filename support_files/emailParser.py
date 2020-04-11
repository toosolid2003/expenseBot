# coding: utf-8
from classes import Expense
import json
def parseFlightEmail(jsonFile):
    '''Parses the data contained in a json file sent by mailparser.io
    Input: filePath
    Output: an expense object with amount and reason'''

    with open('easyjet-2020-04-10.json') as data:
        data = json.load(data)
        data = data[-1]     #we only consider the last element

    exp = Expense()
    exp.amount = data['amount']
    exp.reason = 'flight ' + data['destination']

    #Check if the currency is euro, in which case it conerts amount to CHF and format
    #to only keep 2 decimals

    if data['currency'] == '€':
        exp.amount = float(data['amount']) * 1.03
        exp.amount = "{:.2f}".format(exp.amount)

    #We miss the exp.receipt...
    return exp
