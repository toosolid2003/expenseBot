from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
import telegram
import logging
import time
from dbhelper import DBHelper

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

#Initiating global variables
updater = None
WBS = '000000'
DATA = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':WBS, 'type':'Misc. Travel'}
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = telegram.Bot(TOKEN)
#keybArray = [['Airfare','Business Meals','Lodging'],
#                ['Rental Car', 'Transportation', 'Misc. Travel','Misc. Expenses']]
#KEYBOARD = telegram.ReplyKeyboardMarkup(keybArray, resize_keyboard=True, one_time_keyboard=True)

#Initiating the database
db = DBHelper()
db.setup()

# Database funcntions
#################################################################

def injectDATA():
    '''inject the data contained in the DATA global dict into the sqlite db'''
    global DATA
    global WBS

    # Add the final piece of data: Expense Type
    data_tuple = (DATA['amount'],DATA['date'], DATA['reason'], DATA['status'], WBS, DATA['type'], DATA['blob'])
    db.add_item(data_tuple)
    DATA = {'date':time.strftime("%Y-%m-%d"), 'reason':None,'status':'pending','blob':None,'amount':None,'wbs':WBS, 'type':'Misc. Travel'}


def checkCompletion():
    '''Checks if the DATA dict has all the data to log the expense into the DB.
    Returns a list of missing values for the db.'''

    global DATA
    rest = []
    for key, value in DATA.items():
        if value == None:
            rest.append(key)
    return rest

# Commands
#################################################################

def start(update, context):
    text = "Bienvenue sur ton bot d'expenses. Cela va demenager."
    update.message.reply_text(text)

def wbs(update, context):
    global WBS
    if len(context.args) > 0:
        WBS = context.args[0]
        update.message.reply_text('Your new WBS: {}'.format(WBS))
    else:
        update.message.reply_text('Your current WBS is {}'.format(WBS))

    # Input handlers
#################################################################

# Downloads the receipt picture as a byte array to be stored in the DB
def photoCapture(update, context):
    global DATA

    photoId = update.message.photo[-1]['file_id']
    DATA['blob'] = bot.get_file(photoId).download_as_bytearray()
    # Inject the DATA
    rList = checkCompletion()
    if len(rList) == 0:
        injectDATA()
        update.message.reply_text('I have recorded your data.')
    #else:
        #update.message.reply_text(rList)

def captionCapture(update, context):
    global DATA

    # Capture the photo
    photoCapture(update, context)

    # Get the amount and reason
    data = update.message.caption
    dataList = data.split(',')
    DATA['amount'] = dataList[0]
    DATA['reason'] = dataList[1]

    # Inject the DATA
    rList = checkCompletion()
    if len(rList) == 0:
        injectDATA()
        update.message.reply_text('I have recorded your data.')

def textCapture(update, context):
    global DATA

    data = update.message.text
    dataList = data.split(',')

    if len(dataList) > 1:
        DATA['amount'] = dataList[0]
        DATA['reason'] = dataList[1]

    elif len(dataList) == 1:
        try:
            DATA['amount'] = float(dataList[0])
        except ValueError:
            DATA['reason'] = dataList[0]
    else:
        update.message.reply_text('I cannot really tell which is the amount and which is the reason.')

   # Inject the DATA
    rList = checkCompletion()
    if len(rList) == 0:
        injectDATA()
        update.message.reply_text('I have recorded your data.')
    #else:
    #    update.message.reply_text(rList)


def start_bot():
    global updater
    updater = Updater('994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA', use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(MessageHandler(Filters.caption, captionCapture))
    dispatcher.add_handler(MessageHandler(Filters.text, textCapture))
    dispatcher.add_handler(MessageHandler(Filters.photo, photoCapture))

    updater.start_polling()

    updater.idle()

start_bot()
