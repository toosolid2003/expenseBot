# Source for this script: https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger?icn=post-goi5fncay&ici=post-m7o96jger
import time
from dbhelper import DBHelper
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

#Initiates DB and creates an updater object used in the whole program
db = DBHelper()
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

#Set up a logging function to know when things go south.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)




#Make space for the functions

def start(update, context):
    '''Function to reply to the /start command.'''

    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I'm your expense bot, throw me your expenses and I'll make sure they're logged in IQ Navigator")

def hasPic(update, context):
    '''Stores pic it in data['receipt']'''
    photo_file = update.message.photo[-1].get_file()
    breakpoint()
    photo_file.download('receipt.jpg')
    update.message.reply_text('Nice one. Thanks for the receipt')

def main():
    # Initiate all variables 
    db.setup()
    data = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':'BLFG101X'}

    #Picture handler
    pic_handler = MessageHandler(Filters.document.category("image"), hasPic)
    dispatcher.add_handler(pic_handler)

    #Start long polling
    updater.start_polling()

if __name__=='__main__':
    main()
