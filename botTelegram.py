from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
import telegram
import logging
import time
from classes import DBHelper, Expense

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

#Initiating global variables
updater = None
WBS = 'BFG9000'
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = telegram.Bot(TOKEN)
#keybArray = [['Airfare','Business Meals','Lodging'],
#                ['Rental Car', 'Transportation', 'Misc. Travel','Misc. Expenses']]
#KEYBOARD = telegram.ReplyKeyboardMarkup(keybArray, resize_keyboard=True, one_time_keyboard=True)

#Initiating the classes
db = DBHelper()
exp = Expense()
#Setting up the database
db.setup()

# Database funcntions
#################################################################

def injectDATA(exp):
    '''inject the data contained in the Expense object (exp) into the sqlite db'''

    # Add the final piece of data: Expense Type
    data_tuple = exp.to_tuple()
    db.add_item(data_tuple)

    #Initiate a new expense object
    del exp
    exp = Expense()

def checkCompletion(exp):
    '''Checks if the Expense object  has all the data to log the expense into the DB.
    Returns a list of missing values for the db.'''

    rest = []
    exp.wbs = WBS   #Assign a WBS to the expense now, for lack of better place.
    exp.type = 'Misc. Expense'

    for key, value in exp.__dict__.items():
        if value == None:
            rest.append(key)
    return rest

# Commands
#################################################################

def start(update, context):
    text = "Bienvenue sur ton bot d'expenses. Cela va demenager."
    update.message.reply_text(text)

def wbs(update, context):
    '''Changes the wbs value if it is provided as a parameter 
    Otherwise, displays the current WBS against which expenses are logged'''
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
    '''Capture only the picture into Expense object, as a byte array'''

    photoId = update.message.photo[-1]['file_id']
    exp.receipt = bot.get_file(photoId).download_as_bytearray()
    # Inject the DATA
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')
    #else:
    #    update.message.reply_text(rList)

def captionCapture(update, context):
    '''Captures the data contained in the caption'''


    # Capture the photo
    photoCapture(update, context)

    # Get the amount and reason
    data = update.message.caption
    dataList = data.split(',')
    exp.amount = dataList[0]
    exp.reason = dataList[1]

    # Inject the DATA
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')

def textCapture(update, context):

    data = update.message.text
    dataList = data.split(',')

    if len(dataList) > 1:
        exp.amount = dataList[0]
        exp.reason = dataList[1]

    elif len(dataList) == 1:
        try:
            exp.amount = float(dataList[0])
        except ValueError:
            exp.reason = dataList[0]
    else:
        update.message.reply_text('I cannot really tell which is the amount and which is the reason.')

   # Inject the DATA
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
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
