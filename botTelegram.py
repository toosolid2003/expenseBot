from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
from telegram import Bot
import logging
import time
from classes import *
from functions import *
from selfsubmit import *
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

WBS = 'BLXPB001'
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

# Commands
#################################################################

def start(update, context):
    text = '''Hello there, I'm expenseBot. My sole purpose: making business expenses easy for you to log and track.
No one wants to waste time doing that, so here I am. Type '/help' if you want to know what I can do for you.'''
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

def submit(update, context):
    '''Submit into IQ Navigtor the expenses that are still in pending status'''

    response = submit_expenses(update.message.chat.username)
    update.message.reply_text(response)

def helpmsg(update, context):
    text = '''Do you want to log an expense? Easy, I need 3 things from you:
        - An amount
        - A reason (hotel, restaurant, train ticker, flights)
        - A receipt (a picture of your receipt or a any sort of document.
You can give me these details in any way you want. Eg, "400 eur, hotel California" and then send a receipt.
Or just share a picture of a receipt, with the amount and reason as comments.

Beyond that, you can ask me to do specific things with commands. Type:
   - /wbs XXXXX, where XXXXX is the WBS you want to charge your expenses on. Just type /wbs if you want to display the current wbs being used.
   - /submit to ask me to log all your pending expenses into IQ Navigator.
   - /setup to share with me your username and password for IQ Navigator. This way, I can log expenses on your behalf. You will still have to submit the expense report though.

Alright, now enjoy!'''
    update.message.reply_text(text)

def setup(update, context):
    '''Takes the username and password of a new user'''

    if len(context.args) > 0:
        username = context.args[0]
        password = context.args[1]
        dbuser = userDB()
        dbuser.add_user(update.message.chat.username, username, password)
        update.message.reply_text('Thanks, I have username: {} and password: {}'.format(username, password))
    else:
        update.message.reply_text('Sorry, I did not understand. Make sure you separate the command, the username and the password by a space for me to understand which is which. Eg: /setup myusername mypassword')


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
    update.message.reply_text('You miss :{}'.format(rList))
    if len(rList) == 0:
        injectDATA(exp)
        update.message.reply_text('I have recorded your data.')
def echoText(update, message):
    update.message.reply_text('You said {}'.format(update.message.text))

def setup(bot):
    global exp
    exp = Expense()
    #Initiating global variables
    WBS = 'BLXPB001'
    #Initiating the classes
    db = DBHelper()
    db.setup()
    
    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

    #Registering handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', helpmsg))
    dispatcher.add_handler(CommandHandler('wbs', wbs))
    dispatcher.add_handler(CommandHandler('submit', submit))
    dispatcher.add_handler(CommandHandler('setup', setup))
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
    return dispatcher

def webhook(update, dispatcher):
    dispatcher.process_update(update)
