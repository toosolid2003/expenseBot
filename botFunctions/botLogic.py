#-*- coding: utf-8 -*-
from os import chdir, rename, path
import json
from time import strftime, strptime
from logger.logger import logger
from botClasses.classes import DBHelper
import uuid
import re
from forex_python.converter import CurrencyRates
from datetime import datetime
import csv
from maya import dateparser
import zipfile

db = DBHelper()


#######Decorator for logging ########
#####################################

def decoLog(func):
    def wrapper(*args, **kwargs):
        logger.debug('Using function ' + func.__name__)

        return func(*args, **kwargs)
    return wrapper


####################################
@decoLog
def checkCompletion(dic):
    """
    Checks if the context.user_data dictionnary has all the data necessary to record the expense in the database.

    Input: context.user_data (dictionnary)
    Output: Boolean
    """
    expectedKeys = ['amount','reason','typex','receipt','user']
    missingData = []

    for elt in expectedKeys:
        try:
            if not dic[elt]:
                missingData.append(elt)
        except KeyError:                # in case context.user_data has not create the key yet (new user)
            missingData.append(elt)

    if missingData:
        logger.info(f'Missing: {missingData}')
        return False
    else:
        return True
    

@decoLog
def getAmount(resultList):
    for elt in resultList:
        try:
            return round(float(elt),2)
        except:
            pass

@decoLog
def getType(resultList):
    types = {'accomodation' :['airbnb','apartment','hotel','pension','hostel'],
           'transportation':['taxi','uber','lyft','train','bus','ferry','sbb','eurostar','sncf','thalys'],
   'flight':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
   'car rental':['avis','entreprise','rental car','alamo', 'car rental','car'],
   'food & beverage':['drinks','bar','restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','breakfast'],
   'car expenses':['toll','parking','fuel','highway','public','gas','petrol'],
   'per diem':['perdiem', 'per diem','per diems','perdiems']
   }

    expenseType = 'various'
      #We run through the types dictionnary, getting both the items and the indexes
   # From that, we run through all the elemtns of the results list and see if one of
   # them matches an item in the dictionnary
   # If yes, we we return the index title of the dictionnary list that has the element.

    for title, typeList in types.items(): 
        for elt in resultList: 
            if elt in typeList: 
                expenseType = title

    return expenseType
        

@decoLog
def getCurrency(resultList):
    managedCcy = ['usd','chf','aud','nzd','rub','eur','cad','rub','uah']

    for elt in resultList:
        if elt in managedCcy:
            return elt

def getReason(resultList):

    #Other way: we remove the currency and the amount from the splitted result list
    ccy = getCurrency(resultList)
    if ccy is not None:
        resultList.pop(1)

    resultList.pop(0)

    reason = " ".join(resultList)
    return reason    
   
@decoLog
def parseText(rawText, activeUser):
    '''Parses the raw text data captured by the bot. Turns it into an amount (float) and a reason (string).
    Input: rawText, active user (telegram handle)
    Output: dict of values (amount, reason and type)'''

    #Initiate the dictionnary that will be returned
    values = {'amount':None, 'reason':None, 'typex':None}

    #NEW VERSION: using a regex to parse the raw text sent by user
    resultList = re.split(r'[:,;\s]\s*', rawText.lower())

    #GETTING THE CURRENCY AND AMOUNT
    baseCcy = db.get_ccy(activeUser)
    ccy = getCurrency(resultList)

    if ccy and ccy != baseCcy:
        #get the converstion rate and recalculate the amount
        c = CurrencyRates()
        unroundedAmount = c.convert(ccy.upper(), baseCcy.upper(),getAmount(resultList))
        values['amount'] = round(unroundedAmount, 2)
    else:
        values['amount'] = getAmount(resultList)

    #GETTING THE TYPE AND REASON
    values['typex'] = getType(resultList)
    values['reason'] = getReason(resultList)


    return values

@decoLog
def saveDocument(fileId, telegram_username, bot):
    '''Saves a document on the local disk and returns a filepath to be stored in the database.
    Input: Telegram file_id, telegram_username and Telegram bot instance
    Output: absolute_path_to_file'''

    #Change the current directory to one which www-data has access to
    chdir('/var/www/expenseBot/receipts/')
    #Download the file
    try:
        filename = bot.get_file(fileId).download()
    except Exception as e:
        logger.error('Could not download file %s. Error: %s', fileId, e)

    newFilepath = '/var/www/expenseBot/receipts/' + telegram_username +'/' + filename

    #Move the document to a dedicated folder
    rename(filename, newFilepath)

    return newFilepath

@decoLog
def toMarkdown(expenses):
    '''
    Formats all expenses provided in parameters to be displayed to user.

    Input: list of expenses as tuples, extracted from db
    Output: string with all expenses formatted

    '''
    output = ''
    for expense in expenses:

        #Reformatting the time variable for legibility
        totime = strptime(expense[2], "%Y-%m-%d")
        expenseDate = strftime("%a %d %B", totime)
        output += '- {}, {} {}, {}\n'.format(expenseDate, expense[0], expense[1], expense[3])
    
    return output

@decoLog
def totalPending(expenses):
    '''Calculates the total amount of current pending expenses.
    Input: list of expenses as tuples
    Output: float'''

    total = 0
    for expense in expenses:
        total += expense[0]
        total = round(total, 2)

    return total

@decoLog
def deductType(reason):
   '''
   Deducts the expense type (IQ Navigator categories) based on what has been given as a reason.
   
   Input: context.user_data['reason'] (string)
   Output: expense type (string)
   '''

   #We infer the expense type by confronting the value in exp.reason to a list of possible words
   

   # Types dictionnary
   #These types below for IQ Navigator categories
#   types = {'17819670115' :['hotel','pension','hostel'],
#           '17819672005':['airbnb','apartment'],
#           '17819688948':['train','bus','ferry','sbb','eurostar','sncf','thalys'],
#           '17819688802':['taxi','uber','lyft'],
#   '17819684336':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
#   '107851819':['avis','entreprise','rental car','alamo', 'car rental','car'],
#   '17819687015':['drinks','bar','restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','breakfast'],
#   '17858921758':['toll','parking','fuel','highway','public','gas','petrol'],
#   '17819687871':['perdiem', 'per diem','per diems','perdiems']
#   }
#
#   typex = '17819687102'

   types = {'accomodation' :['airbnb','apartment','hotel','pension','hostel'],
    'transportation':['taxi','uber','lyft','train','bus','ferry','sbb','eurostar','sncf','thalys'],
    'flight':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
    'car rental':['avis','entreprise','rental car','alamo', 'car rental','car'],
    'food & beverage':['drinks','bar','restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','breakfast'],
    'car expenses':['toll','parking','fuel','highway','public','gas','petrol'],
    'per diem':['perdiem', 'per diem','per diems','perdiems'],
    }

   typex = 'various'

   #The magic loop, where the deduction happens
   for accType, typeList in types.items():
       for elt in typeList:
           if elt in reason.lower():
               typex = accType


   return typex

@decoLog
def injectData(dico):
    """
    Inject the expense data contained in the dictionnary into the database.

    Input: dictionnary with the data (context.user_data)
    Output: uid of the expense
    """
    dico['uid'] = str(uuid.uuid4())
    dico['date'] = strftime("%Y-%m-%d")
    dico['status'] = 'pending'
    dico['currency'] = db.get_ccy(dico['user'])

    data_tuple = (
        dico['uid'], 
        dico['amount'], 
        dico['currency'], 
        dico['date'], 
        dico['reason'], 
        dico['status'], 
        dico['typex'], 
        dico['receipt'], 
        dico['user'],
        )

    try:
        db.add_item(data_tuple)
        logger.info('Expense %s added to the databse for user %s', dico['uid'], dico['user'])
        db.add_datapoint(dico['user'], 'Expense added', dico['uid'])
        return dico['uid']

    except Exception as e:
        logger.error('Error while injecting expense into database (%s) for %s', e, dico['user'])
        pass