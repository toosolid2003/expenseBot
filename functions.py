#coding: utf-8
from PIL import Image
from io import BytesIO
import os

def createImagePath(exp):
    '''Creates an image from the byte array stored in the expense object (exp.receipt).
    The path to this image can then be sent to IQ Navigator as a receipt.
    Input: an expense object
    Output: path to the image file'''

    img = Image.open(BytesIO(exp.receipt))
    filename = 'receipt.png'
    img.save(filename)

    filepath = os.getcwd() + '/' + filename

    return filepath

def checkCompletion(exp):
    '''Checks if the Expense object has all the data to log the expense into the DB.
    Returns a list of missing values for the db.'''

    rest = []
    for key, value in exp.__dict__.items():
        if value == None:
            rest.append(key)
    return rest

def parseText(rawText):
    '''Parses the raw text data captured by the bot. Turns it into an amount (float) and a reason (string).
    If a currency is detected, it calls the convertAmount function.
    Input: rawText, expense object
    Output: expense object with amount and reason attributes filled'''


    #Split the text according to a pre-determined separator
    sepList = [',','-',':',';']
    parsedText = []

    #Step 1 - Split the raw text into a list of elements
    for sep in sepList:
        if sep in rawText:
            parsedText = rawText.split(sep)

    #Step 3 - Assign amount and reason
    amount = None
    reason = None
    for elt in parsedText:
        try:
            amount = float(elt)
        except ValueError:
            reason = elt.strip()

    #Step 4 - Detect a potential currency
#    ccyList = ['eur','chf','usd','nzd','aud','cad','gbp']
#    for ccy in ccyList:
#        for elt in parsedText:
#            if ccy == elt:
#                #convertAmount(ccy, amount)
#                print('Found currency: {}'.format(elt))
#                parsedText.remove(ccy)
    #Step 5 - Assign the remaining text to the reason attribute of expense object

    return amount, reason

def convertAmount(ccy, amount):
    '''Converts an amount from a source ccy to a target ccy.
    Input: target ccy (str)  and amount (float)
    Output: converted amount (float)'''

    ccyDict = {'eur':1.04,'usd': 1.1}
    convertedAmount = amount * ccy
    #tbc
    return convertAmount
