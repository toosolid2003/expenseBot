from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, JobQueue
import telegram
from telegram import Bot
import datetime
import logging
import time
from botClasses.classes import *
from botFunctions.botCommands import *
from botFunctions.botLogic import *
from botFunctions.botJobs import iqnExpensesLog, testJob

#from selfsubmit import *
#logging.basicConfig(filename='/var/www/expenseBot/log/bot.log', format='%(levelname)s - %(message)s', level=logging.DEBUG)

logging.basicConfig(filename='/var/www/expenseBot/log/bot.log', format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    token = token.replace('\n','')

#TOKEN = '994986692:AAF2wlYCT9_KIbLVxCRLNVVNfQMM9NJJJmA'
bot = Bot(token)
#Initiating the classes
db = DBHelper()
db.setup()
userdb = userDB()
userdb.setup()
db = DBHelper()

# Database funcntions
#################################################################

def injectDATA(exp):
    '''inject the data contained in the Expense object (exp) into the sqlite db'''

    #Convert to a tuple for SQL injection
    data_tuple = exp.to_tuple()
    try:
        db.add_item(data_tuple)
        logging.info('Expense properly injected for %s', exp.user)
    except Exception as e:
        logging.info('Error while injecting expense into database: %s', e)

    #Resetting the expense object
    exp.amount = None
    exp.receipt = None
    exp.reason = None

# Input handlers
#################################################################

# Downloads the receipt picture as a byte array to be stored in the DB
def photoCapture(update, context):
    '''Capture only the picture into Expense object, as an absolute path to the
    downloaded file.'''

    global exp

    exp.user = update.message.chat.username

    #Is is a photo?
    try:
        photoId = update.message.photo[-1]['file_id']
        exp.receipt = saveDocument(photoId, exp.user, bot)
    #or a document (pdf, etc.)?
    except IndexError:
        fileId = update.message.document['file_id']
        exp.receipt = saveDocument(fileId, exp.user, bot)
    # Inject the DATA if expense object is complete
    try: 
        exp.wbs = userdb.get_wbs(exp.user)
    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")

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
    exp.user = update.message.chat.username
    try: 
        exp.wbs = userdb.get_wbs(exp.user)
    except KeyError:
       update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")


    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('Thanks, I have recorded your expense.')

def textCapture(update, context):

    global exp

    rawText = update.message.text
    
    # Parse the text
    parsedDict = parseText(rawText)
    if parsedDict['amount']:
        exp.amount = parsedDict['amount']
    if parsedDict['reason']:
        exp.reason = parsedDict['reason']
    if exp.reason:
        exp = deductType(exp)

     # Inject the DATA
    exp.user = update.message.chat.username
    try: 
       exp.wbs = userdb.get_wbs(exp.user)
    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")

    rList = checkCompletion(exp)
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('Thanks for this, I got your expense.')

def echoText(update, message):
    update.message.reply_text('You said {}'.format(update.message.text))

def setup(bot):
    global exp
    exp = Expense()

    #Initiating the classes
    db = DBHelper()
    db.setup()
    
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

    #Initiate the "setup" conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states = {EMAIL: [MessageHandler(Filters.text, email)],
            IQUSERNAME: [MessageHandler(Filters.text, iqusername)],
            IQPASSWORD: [MessageHandler(Filters.text, iqpassword)],
            WBS: [MessageHandler(Filters.text, wbsSetup)]
            },
        fallbacks=[CommandHandler('stopit', stopit)]
        )


    #Registering handlers
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('help', helpmsg))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(CommandHandler('submit', submit))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(MessageHandler(Filters.caption, captionCapture))
    dispatcher.add_handler(MessageHandler(Filters.text, textCapture))
    dispatcher.add_handler(MessageHandler(Filters.photo, photoCapture))
    dispatcher.add_handler(MessageHandler(Filters.document, photoCapture))

    #Initiate the job_queue performed by the server
#    jobs = dispatcher.job_queue
    j = JobQueue()
    j.set_dispatcher(dispatcher)
    jobTime = datetime.timedelta(minutes=30)
    job_logExpenses = j.run_repeating(iqnExpensesLog,jobTime)
    j.start()

    return dispatcher

def webhook(update, dispatcher):
    dispatcher.process_update(update)
