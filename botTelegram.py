from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
import telegram
import logging
import time
from classes import *
from functions import *

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

#Initiating global variables
updater = None
WBS = 'BLXPB001'
TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = telegram.Bot(TOKEN)

#Initiating the classes
db = DBHelper()
#exp = Expense()
#Setting up the database
db.setup()


# Database funcntions
#################################################################

def injectDATA(exp):
    '''inject the data contained in the Expense object (exp) into the sqlite db'''

    #Convert to a tuple for SQL injection
    data_tuple = exp.to_tuple()
    db.add_item(data_tuple)

    #Resetting the expense object
    exp.amount = None
    exp.receipt = None
    exp.reason = None

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
    '''Capture only the picture into Expense object, as an absolute path to the
    downloaded file.'''

    global exp

    #Is is a photo?
    try:
        photoId = update.message.photo[-1]['file_id']
        exp.receipt = saveDocument(photoId, bot)
    #or a document (pdf, etc.)?
    except IndexError:
        fileId = update.message.document['file_id']
        exp.receipt = saveDocument(fileId, bot)
    # Inject the DATA if expense object is complete
    exp.user = update.message.chat.username
    exp.wbs = WBS
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')

    #else:
    #    update.message.reply_text(rList)

def captionCapture(update, context):
    '''Captures the data contained in the caption'''

    global exp
    # Capture the photo
    photoCapture(update, context)

    # Get the amount, reason and deduct type
    rawText = update.message.caption

    parsedDict = parseText(rawText)
    if parsedDict['amount']:
        exp.amount = parsedDict['amount']
    if parsedDict['reason']:
        exp.reason = parsedDict['reason']
    if exp.reason:
        exp = deductType(exp)

    # Inject the DATA
    exp.wbs = WBS
    exp.user = update.message.chat.username
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')

def textCapture(update, context):

    global exp

    rawText = update.message.text

    parsedDict = parseText(rawText)
    if parsedDict['amount']:
        exp.amount = parsedDict['amount']
    if parsedDict['reason']:
        exp.reason = parsedDict['reason']
    if exp.reason:
        exp = deductType(exp)

 # Inject the DATA
    exp.wbs = WBS
    exp.user = update.message.chat.username
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')
   #else:
    #    update.message.reply_text(rList)


def start_bot():
    global updater
    global exp
    exp = Expense()
    updater = Updater('994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA', use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(MessageHandler(Filters.caption, captionCapture))
    dispatcher.add_handler(MessageHandler(Filters.text, textCapture))
    dispatcher.add_handler(MessageHandler(Filters.photo, photoCapture))
    dispatcher.add_handler(MessageHandler(Filters.document, photoCapture))

    updater.start_polling()

    updater.idle()

start_bot()
