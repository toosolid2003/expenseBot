from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, JobQueue, CallbackContext
import telegram
from telegram import Bot
import datetime
import time
from botClasses.classes import *
from botFunctions.botCommands import *
from botFunctions.botLogic import *
from botFunctions.botJobs import iqnExpensesLog, submitJob 
from logger.logger import logger
import logging
import uuid

#logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
#logger = logging.getLogger(__name__)

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

# Input handlers
#################################################################

# Downloads the receipt picture as a byte array to be stored in the DB
def photoCapture(update, context):
    '''
    Downloads the picture and saves the path to file in context.user_data
    '''

    #global exp

    user = update.message.chat.username

    #Is is a photo?
    try:
        photoId = update.message.photo[-1]['file_id']
        context.user_data['receipt'] = saveDocument(photoId, user, bot)

    #or a document (pdf, etc.)?
    except IndexError:
        fileId = update.message.document['file_id']
        context.user_data['receipt'] = saveDocument(fileId, user, bot)

    #Logging and error for all other kinds of exceptions
    except Exception as e:
        logger.error('Could not save the attached document or photo for %s. Error: %s', exp.user, e)

    # Inject the DATA if expense object is complete
    #First the user
    context.user_data['user'] = user

    #Second the wbs
    try: 
        context.user_data['wbs'] = userdb.get_wbs(user)
    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")
    except Exception as e:
        logger.error('Problem while trying to recover the wbs from the database. Error: %s', e)

    #Third check for completion
    isComplete = checkCompletion(context.user_data)
    if isComplete:
        logger.info('Expense data is complete. Ready for database injection.')
        injectData(context.user_data)
        resetDic(context.user_data)
        update.message.reply_text('Thanks, I have recorded your expense.')



def captionCapture(update, context):
    '''Captures the data contained in the caption'''

    #global exp

    # Capture the photo
    photoCapture(update, context)

    # Parse the text: adds amount + reason and type if amount and reason in the raw text
    tempDict = parseText(update.message.caption, update.message.chat.username)

    # Feeding the missing element in context.user_data
    if tempDict['amount'] != None:
        context.user_data['amount'] = tempDict['amount']

    if tempDict['reason'] != None:
        context.user_data['reason'] = tempDict['reason']
        context.user_data['typex'] = tempDict['typex']

    # Add the telegram handle to context.user_data
    context.user_data['user'] = update.message.chat.username

    # Add the wbs to context.user_data
    try: 
       context.user_data['wbs'] = userdb.get_wbs(context.user_data['user'])
    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")
    except Exception as e:
        logger.error('Problem while trying to recover the wbs from the database. Error: %s', e)

    #Check for completion and inject data if positive
    isComplete = checkCompletion(context.user_data)
    if isComplete:
        logger.info('Expense data is complete. Ready for database injection.')
        injectData(context.user_data)
        resetDic(context.user_data)
        update.message.reply_text('Thanks for this, I got your expense.')

def textCapture(update, context):

    #global exp

    rawText = update.message.text
    
    # Parse the text: adds amount + reason and type if amount and reason in the raw text
    tempDict = parseText(rawText, update.message.chat.username)

    # Feeding the missing element in context.user_data
    if tempDict['amount'] != None:
        context.user_data['amount'] = tempDict['amount']

    if tempDict['reason'] != None:
        context.user_data['reason'] = tempDict['reason']
        context.user_data['typex'] = tempDict['typex']

    # Add the telegram handle to context.user_dat
    context.user_data['user'] = update.message.chat.username

    # Add the wbs to context.user_data
    try: 
       context.user_data['wbs'] = userdb.get_wbs(context.user_data['user'])
    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")
    except Exception as e:
        logger.error('Problem while trying to recover the wbs from the database. Error: %s', e)

    isComplete = checkCompletion(context.user_data)
    if isComplete:
        logger.info('Expense data is complete. Ready for database injection.')
        injectData(context.user_data)
        resetDic(context.user_data)
        update.message.reply_text('Thanks for this, I got your expense.')


def setup(bot):
    #global exp
    #exp = Expense()

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
            CURRENCY: [MessageHandler(Filters.text, currency)],
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
    j = JobQueue()
    j.set_dispatcher(dispatcher)
    jobTime = datetime.timedelta(minutes=30)
    job_logExpenses = j.run_repeating(iqnExpensesLog,jobTime)
    j.start()



    return dispatcher

def webhook(update, dispatcher):
    dispatcher.process_update(update)
