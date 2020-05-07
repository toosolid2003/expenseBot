#-*- coding: utf-8 -*-
import os
import json
from botClasses.classes import Expense, DBHelper, userDB
import time
import logging

userdb = userDB()

def checkCompletion(exp):
    '''Checks if the Expense object has all the data to log the expense into the DB.
    Returns a list of missing values for the db.'''

    rest = []
    try:
        for key, value in exp.__dict__.items():
            if value == None:
                rest.append(key)
    except Exception as e:
        logging.error('Could not perform checkCompletion. Error: %s',e)

    return rest

def parseText(rawText, activeUser):
    '''Parses the raw text data captured by the bot. Turns it into an amount (float) and a reason (string).
    Input: rawText, active user (telegram handle)
    Output: dict of values (amount and reason)'''

    #Initiate the dictionnary that will be returned
    values = {'amount':None, 'reason':None}

    #Initiate the base currency variable
    baseCcy = userdb.get_ccy(activeUser)

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
            if conversionRate(elt,'CHF'):
                conversionFactor = conversionRate(elt,'CHF')

            #Remove the ccy from the elt to prepare for float assignment
            elt = convertUpdateElement(elt)

            try:
                values['amount'] = float(elt)
            except ValueError:
                values['reason'] = elt.strip()

    else:                       #If parsedText IS an empty list = if there is just 1 element in rawText
        if conversionRate(rawText,'CHF'):
            conversionFactor = conversionRate(rawText,'CHF')
        rawText = convertUpdateElement(rawText)

        try:
            values['amount'] = float(rawText)
        except ValueError:
            values['reason'] = rawText.strip()

    #Multiple anount by conversion factor before return - only if we could extract the amount from rawText
    if values['amount']:
        values['amount'] = values['amount'] * conversionFactor

    return values

def conversionRate(parsingElt, baseCcy):

    '''Converts an amount from CHF to a target ccy.
    Input: parsing element, base currency (strings)
    Output: conversion rate as float

    Returns None if no currency has been found in the parsed element'''


    #Identify the dict corresponding to the base currency
    allCcy = {'CHF': {'eur':1.06,'usd':0.97,'nzd':0.59,'aud':0.61,'cad':0.69,'gbp':1.2},
            'EUR': {'chf':0.95, 'usd':0.92, 'nzd':0.56, 'aud':0.6, 'cad':0.66, 'gbp':1.15}
            }
    ccyDict = allCcy[baseCcy]

    #Identify the  conversion rate
    for ccy in ccyDict.keys():
        if ccy in parsingElt.lower():
            return ccyDict[ccy]

def convertUpdateElement(parsingElt):
    '''Substract the currency denominator from the parsed element to prepare it for
    type change withe float'''

    ccyDict = {'eur':1.06,'usd':0.97,'nzd':0.59,'aud':0.61,'cad':0.69,'gbp':1.2}

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

def saveDocument(fileId, telegram_username, bot):
    '''Saves a document on the local disk and returns a filepath to be stored in the database.
    Input: Telegram file_id, telegram_username and Telegram bot instance
    Output: absolute_path_to_file'''

    #Change the current directory to one which www-data has access to
    os.chdir('/var/www/expenseBot/receipts/')
    #Download the file
    try:
        filename = bot.get_file(fileId).download()
    except Exception as e:
        logging.error('Could not download file %s. Error: %s', fileId, e)

    newFilepath = '/var/www/expenseBot/receipts/' + telegram_username +'/' + filename

    #Move the document to a dedicated folder
    os.rename(filename, newFilepath)

    return newFilepath

def toMarkdown(expenses):
    '''
    Formats all expenses provided in parameters to be displayed to user.

    Input: list of expenses as tuples, extracted from db
    Output: string with all expenses formatted

    '''
    output = ''
    for expense in expenses:

        #Reformatting the time variable for legibility
        totime = time.strptime(expense[1], "%d-%m-%Y")
        expenseDate = time.strftime("%a %d %B", totime)
        output += '- {}, {} CHF, {}\n'.format(expenseDate, expense[0], expense[2])
    
    return output

def totalPending(expenses):
    '''Calculates the total amount of current pending expenses.
    Input: list of expenses as tuples
    Output: float'''

    total = 0
    for expense in expenses:
        total += expense[0]

    return total

def deductType(expense):
   '''Deducts the expense type (IQ Navigator categories) based on what has been given to the exp.reason attribute'''

   #We infer the expense type by confronting the value in exp.reason to a list of possible words
   
   ### The Hotel accomodation entry has en em-dash the needs to be replicated in the types dictionnary
   emDash = u'\u2014'
   accomodationHotel = "Accomodation {} Hotal".format(emDash)

   # Types dictionnary
   types = {'17819670115' :['hotel','airbnb','pension','hostel'],
           '17819672005':['airbnb','apartment'],
           '17819688948':['train','bus','ferry','sbb','eurostar','sncf','thalys'],
           '17819688802':['taxi','uber','lyft'],
   '17819684336':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
   '107851819':['avis','entreprise','rental car','alamo'],
   '17819687015':['drinks','bar','restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','breakfast'],
   '17819686820':['toll','parking','fuel','highway','public','gas','petrol'],
   '17819687871':['perdiem', 'per diem','per diems','perdiems']
   }

   #The magic loop, where the deduction happens
   for accType, typeList in types.items():
       for elt in typeList:
           if elt in expense.reason.lower():
               expense.type = accType

   return expense
