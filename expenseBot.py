# Source for this script: https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger?icn=post-goi5fncay&ici=post-m7o96jger
import time
from dbhelper import DBHelper
<<<<<<< HEAD
=======
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import telegram
>>>>>>> telegramLib

#Initiates DB and creates an updater object used in the whole program
db = DBHelper()
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
#Make space for the functions

def hasPic(update, context):
    '''Stores pic it in data['receipt']'''
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('receipt.jpg')
    update.message.reply_text('Nice one. Thanks for the receipt')

def main():
    # Initiate all variables 
    db.setup()
    data = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':'BLFG101X'}
    bot = telegram.Bot(token=TOKEN)
    offset = None

    # Start of the loop
    while True:
        # Get latest update
        updates = bot.getUpdates(offset, timeout=15)                        # Tiemout set to 15 to avoid a bug in the Telegram library
        if len(updates) > 0:
            lastUpdateId = len(updates) - 1

            # Get the photo
            photoId = updates[lastUpdateId].message.photo[2]['file_id']
            data['blob'] = bot.get_file(photoId).download_as_bytearray()

            # Get the reson and amount from the photo caption
            text = updates[lastUpdateId].message.caption
            expenseData = text.split(sep=',')
            data['amount'] = float(expenseData[0])
            data['reason'] = expenseData[1]

            # Inject into the database
            data_tuple = (data['amount'], data['date'], data['reason'], data['status'], data['wbs'], data['blob'])
            db.add_item(data_tuple)

            # Send feedback
            chat_id = updates[lastUpdateId].message.chat_id
            bot.send_message(chat_id, text="Expense recorded, bro.")

            # Update offset to avoid getting all updates every time
            offset = updates[lastUpdateId].update_id + 1
        time.sleep(1)

if __name__=='__main__':
    main()
