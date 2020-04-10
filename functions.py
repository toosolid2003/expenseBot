#coding: utf-8
from PIL import Image
from io import BytesIO
import os
import json
from classes import Expense
import time

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
    Input: rawText
    Output: dict of values (amount and reason)'''

    #Initiate the dictionnary that will be returned
    values = {'amount':None, 'reason':None}

    #Split the text according to a pre-determined list of separators
    sepList = [',','-',':',';']
    parsedText = []
    conversionFactor = 1
    #Step 1 - Split the raw text into a list of elements
    for sep in sepList:
        if sep in rawText:
            parsedText = rawText.split(sep)

    #Step 2 - Assign amount and reason
    if parsedText:              #If parsedText list IS NOT empty = if there is more than 1 element in rawText
        for elt in parsedText:
            #Detecte a potential currency in the parsedText and update conversionFactor
            if conversionRate(elt):
                conversionFactor = conversionRate(elt)

            #Remove the ccy from the elt to prepare for float assignment
            elt = convertUpdateElement(elt)

            try:
                values['amount'] = float(elt)
            except ValueError:
                values['reason'] = elt.strip()

    else:                       #If parsedText IS an empty list = if there is just 1 element in rawText
        if conversionRate(rawText):
            conversionFactor = conversionRate(rawText)
        rawText = convertUpdateElement(rawText)

        try:
            values['amount'] = float(rawText)
        except ValueError:
            values['reason'] = rawText.strip()

    #Multiple anount by conversion factor before return - only if we could extract the amount from rawText
    if values['amount']:
        values['amount'] = values['amount'] * conversionFactor

    return values

def conversionRate(parsingElt):

    '''Converts an amount from CHF to a target ccy.
    Returns None if no currency has been found in the parsed element'''

    ccyDict = {'eur':0.95,'usd':1.03,'nzd':1.71,'aud':1.65,'cad':1.44,'gbp':0.83}

    for ccy in ccyDict.keys():
        if ccy in parsingElt.lower():
            return ccyDict[ccy]

def convertUpdateElement(parsingElt):
    '''Substract the currency denominator from the parsed element to prepare it for
    type change withe float'''

    ccyDict = {'eur':0.95,'usd':1.03,'nzd':1.71,'aud':1.65,'cad':1.44,'gbp':0.83}

    tempElt = parsingElt.lower()
    for ccy in ccyDict.keys():
        if ccy in tempElt:
            parsingElt = parsingElt.replace(ccy,'')

    return parsingElt

def parseFlightEmail(jsonFile):
    '''Parses the data contained in a json file sent by mailparser.io
    Input: filePath.json
    Output: an expense object with amount and reason'''

    with open(jsonFile) as data:
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

def saveDocument(fileId, bot):
    '''Saves a document on the local disk and returns a filepath to be stored in the database.
    Input: Telegram file_id and Telegram bot instance
    Output: absolute_path_to_file'''

    #Create a filename
    timestamp = int(time.time())
    filepath = 'receipts/'+'doc_'+str(timestamp)+'.pdf'

    #Download the file
    bot.get_file(fileId).download(filepath)

    return filepath
