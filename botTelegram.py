from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
import telegram
import logging
import time
from dbhelper import DBHelper

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

#Initiating global variables
updater = None
DATA = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs': None}
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = telegram.Bot(TOKEN)

#Initiating the database
db = DBHelper()
db.setup()

def start(update, context):
    text = "Bienvenue sur ton bot d'expenses. Cela va demenager."
    update.message.reply_text(text)

def wbs(update, context):
    update.message.reply_text('Your current WBS: {}'.format(context.args[0]))

def getPhoto(update):
    global DATA
    photoId = update.message.photo[-1]['file_id']
    DATA['blob'] = bot.get_file(photoId).download_as_bytearray()

    return DATA

def captionCapture(update, context):
    global DATA

    # Capture the photo
    getPhoto(update)

    # Get the amount and reason
    data = update.message.caption
    dataList = data.split(',')
    DATA['amount'] = dataList[0]
    DATA['reason'] = dataList[1]

    # Confirm everything went well
    update.message.reply_text('Your data has been captured, thanks!')

    return DATA

def enter(update, context):
    '''A callback to enter the DATA in the database'''
    data_tuple = (DATA['amount'],DATA['date'], DATA['reason'], DATA['status'], DATA['wbs'], DATA['blob'])
    db.add_item(data_tuple)

def start_bot():
    global updater
    updater = Updater('994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA', use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(CommandHandler('enter', enter))
    dispatcher.add_handler(MessageHandler(Filters.caption, captionCapture))

    updater.start_polling()

    updater.idle()

start_bot()

