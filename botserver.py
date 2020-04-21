from flask import Flask
from flask import request
from telegram import Update, Bot
from telegram.ext import Dispatcher
from botTelegram import *
from botClasses.classes import DBHelper
#from functions import *
import json
import os
import logging

#Get the TOKEN for the PRODUCTION bot
with open('bot.token', 'r') as fichier:
    TOKEN = fichier.read()
bot = Bot(TOKEN)

dispatcher = setup(bot)   


app = Flask(__name__)
db = DBHelper()

def decodeUpdate(msg, bot):
    decodedMsg = msg.decode('utf8')
    data = decodedMsg.replace('\\n','')
    update = Update.de_json(json.loads(data), bot)
    return update


@app.route("/", methods=["POST","GET"])
def hello():
    #Convert the binary data coming from Telegram into a string
    #print(request.data)
    #Create an Update object to send to webhook() for processing
    if request.data:
        update = decodeUpdate(request.data, bot)
        if update is not None:
            webhook(update, dispatcher)
    return ''


if __name__== '__main__':

    app.run(host='0.0.0.0')
