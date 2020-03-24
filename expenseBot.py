# Source for this script: https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger?icn=post-goi5fncay&ici=post-m7o96jger

import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)

# Basic functions
def get_url(url):

    response = requests.get(url)
    content = response.content.decode('utf-8')
    return content

def getJsonFromUrl(url):
    '''Gets a string response from Requests and parse it into a dictionnary'''
    content = get_url(url)
    js = json.loads(content)
    return js

# Functions to interact with the API
def sendMsg(text, chatId):
    '''Sends a message to the bot.'''

    text = urllib.parse.quote_plus(text)
    url = URL + 'sendMessage?text={}&chat_id={}'.format(text, chatId)
    get_url(url)

def getUpdates(offset=None):
    '''Get the latest updates from Telegram'''
    url = URL + 'getUpdates?timeout=100'
    if offset:
        url += '&offset={}'.format(offset)
    js = getJsonFromUrl(url)
    return js

def getfileId(updates, lastUpdateId):
    '''Extracts the fie Id of the high-definition pciture we want to save.
    Returns a string, the fileId'''

    fileId = updates['result'][lastUpdateId]['message']['photo'][2]['file_id']
    return fileId

def downloadPic(file_id):
    '''Download a picture from the Telegram API and returns a BLOB ready for the database'''
    #Get the file path fron Telegram API
    url = URL + 'getFile?file_id={}'.format(file_id)
    answer = getJsonFromUrl(url)
    filePath = answer['result']['file_path']

    #Download the file from Telegram API, different URL
    urlDownload = 'https://api.telegram.org/file/bot' + TOKEN + '/' + filePath
    photo = requests.get(urlDownload)

    return photo.content

def hasPicture(updates, lastUpdateId):
    '''Checks if a new message has a picutre in it. In which case, it sends back True'''

    try:
        updates['result'][lastUpdateId]['message']['photo']
        return True
    except KeyError:
        return False

def main():
    # Initiate all variables 
    db.setup()
    lastUpdateId = 0
    offset = None
    data = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':'BLFG101X'}

    #Loop through last update to determine what's the best action
    while True:
        updates = getUpdates(offset)
        if len(updates['result']) > 0:
                lastUpdateId = len(updates['result']) - 1
                chat_id = updates['result'][lastUpdateId]['message']['chat']['id']

                if hasPicture(updates, lastUpdateId):
                    fileId = getfileId(updates, lastUpdateId)
                    data['blob'] = downloadPic(fileId)
                else:
                    msgContent = updates['result'][lastUpdateId]['message']['text']
                    #try to convert it as float - in case it's a number
                    try:
                        data['amount'] = float(msgContent)
                        sendMsg('Got your amount', chat_id)
                    except:
                        data['reason'] = msgContent
                        sendMsg('Got the reason', chat_id)

                #Need to get the last update_id to pass it as offset number on the next call for updates
                offset = updates['result'][lastUpdateId]['update_id'] + 1

                #Create the data tuple and inject it in the DB
                if data['amount'] and data['reason'] and data['blob']:
                    data_tuple = (data['amount'], data['date'], data['reason'],data['status'], data['wbs'], data['blob'])
                    try:
                        db.add_item(data_tuple)
                        sendMsg('All good bro, expense recorded.', chat_id)
                        #Reinitialise the data dictionnary
                        data = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':'BLFG101X'}
                    except:
                        sendMsg('I ran into an issue logging the expense, sorry', chat_id)
                else:
                    continue
        time.sleep(0.5)

if __name__=='__main__':
    main()
