from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, JobQueue
import telegram
from telegram import Bot
import logging
import time
from botClasses.classes import *
from botFunctions.botCommands import *
from botFunctions.botLogic import *
from selfsubmit import *
#from functions.telegramFunction import *

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = Bot(TOKEN)
db = DBHelper()

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
    exp.type = None

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
    exp.wbs = context.user_data['wbs']
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('Thanks, I have recorded your expense.')

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
    exp.wbs = context.user_data['wbs']
    exp.user = update.message.chat.username
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('Thanks, I have recorded your expense.')

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
    exp.wbs = context.user_data['wbs']
    exp.user = update.message.chat.username
    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('Thanks, got it.')

def echoText(update, message):
    update.message.reply_text('You said {}'.format(update.message.text))

def setup(bot):
    global exp
    exp = Expense()
    #Initiating global variables
    #WBS = 'BLXPB001'
    #Initiating the classes
    db = DBHelper()
    db.setup()
    
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
 #   jobQ = JobQueue()
  #  jobQ.set_dispatcher(dispatcher)


    #Registering handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', helpmsg))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(CommandHandler('submit', submit))
    dispatcher.add_handler(CommandHandler('setup', setUp))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(MessageHandler(Filters.caption, captionCapture))
    dispatcher.add_handler(MessageHandler(Filters.text, textCapture))
    dispatcher.add_handler(MessageHandler(Filters.photo, photoCapture))
    dispatcher.add_handler(MessageHandler(Filters.document, photoCapture))

#    updater.start_webhook(listen='134.209.202.182',
#            key= '/etc/letsencrypt/live/expensebot.net/privkey.pem',
#            cert='/etc/letsencrypt/live/expensebot.net/fullchain.pem',
#            port=443)
#    #updater.start_polling()
#
#    updater.idle()
    
    #Running the job_queue
#    job_minute = jobQ.run_repeating(jobMinute, interval=60, first=0)

    return dispatcher

def webhook(update, dispatcher):
    dispatcher.process_update(update)
