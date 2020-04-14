from flask import Flask
from flask import request
from botTelegram import *
from telegram import Update
import json
import logging


logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = Bot(TOKEN)


app = Flask(__name__)
dispatcher = setup(bot)

@app.route("/", methods=["POST","GET"])
def hello():
    #Convert the binary data coming from Telegram into a string
    updateData = request.data.decode('utf8')
    #data = json.loads(data)

    #Create an Update object to send to webhook() for processing
    update = Update.de_json(json.loads(updateData), bot)
    webhook(update, dispatcher)
    print(update)
    return 'Webhook ok'

if __name__== '__main__':
    app.run(host='0.0.0.0')
