# Source for this script: https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger?icn=post-goi5fncay&ici=post-m7o96jger

import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)

def get_url(url):

    response = requests.get(url)
    content = response.content.decode('utf-8')
    return content

def getJsonFromUrl(url):
    '''Gets a string response and parsed it into a dictionnary'''

    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    '''Gets the latest updates from the chatbot. Offset is a message id.
    We are telling the API not send updates older than the offset id.'''

    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = getJsonFromUrl(url) 
    return js

def sendMsg(text, chatId):
    '''Sends a message to the bot.'''
    
    text = urllib.parse.quote_plus(text)
    url = URL + 'sendMessage?text={}&chat_id={}'.format(text, chatId)
    get_url(url)

def getLastChat(updates):
    '''Extracts last chat id and content'''

    numUpdates = len(updates['result'])
    lastUpdate = numUpdates - 1
    text = updates['result'][lastUpdate]['message']['text']
    chatId = updates['result'][lastUpdate]['message']['chat']['id']
    return (text, chatId)

def getLastUpdateId(updates):
    updates_ids = []
    for update in updates['result']:
        updates_ids.append(int(update['update_id']))
    return max(updates_ids)

def handle_updates(updates):

    for update in updates['result']:
        try:
            text = update['message']['text']
            chat = update['message']['chat']['id']
            items = db.get_items()

            if text in items:
                db.delete_item(text)
                items = db.get_items()
            else:
                db.add_item(text)
                items = db.get_items()

            message = "\n".join(items)
            sendMsg(message, chat)

        except  KeyError:
            pass

def main():
    
    db.setup()
    lastUpdateId = None

    while True:
        updates = get_updates(lastUpdateId)
        if len(updates['result']) > 0:
            lastUpdateId = getLastUpdateId(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__=='__main__':
    main()
