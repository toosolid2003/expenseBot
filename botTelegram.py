from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, JobQueue, CallbackContext
from telegram import Bot
import datetime
from botClasses.classes import *
from botFunctions.botCommands import *
from botFunctions.botLogic import *
from botFunctions.botJobs import iqnExpensesLog, submitJob 
from logger.logger import logger

#################################################################
# Constants
#################################################################

#Regular expression to identify a new expense. Not used yet.
regex = r"[0-9]+[.]?[0-9]*[\s]?([a-z]{3})?[,.;:]{1}[\s*][a-zA-Z0-9]*"

#################################################################
# Input handlers
#################################################################

# Downloads the receipt picture or documents and stores the filepath to document in the db
@inputTrack
def photoCapture(update, context):
    '''
    Downloads the picture and saves the path to file in context.user_data
    '''


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
        logger.error('Could not save the attached document or photo for %s. Error: %s', user, e)

    # Inject the DATA if expense is complete
    #First the user
    context.user_data['user'] = user

    #Second the wbs
    try: 
#        context.user_data['wbs'] = db.get_wbs(user)
        context.user_data['wbs'] = '000001'

    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")
    except Exception as e:
        logger.error('Problem while trying to recover the wbs from the database. Error: %s', e)

    #Third check for completion
    isComplete = checkCompletion(context.user_data)
    if isComplete:
        logger.info('Expense data is complete. Ready for database injection.')
        expId = injectData(context.user_data)     
        update.message.reply_text('''Thanks, I have recorded your expense correctly.''')
        context.user_data.clear()


@inputTrack
def textCapture(update, context):

    #Check where the text to parse comes from, text or caption.
    if update.message.text != None:
        rawText = update.message.text
    elif update.message.caption:
        rawText = update.message.caption
        photoCapture(update, context)

    # Parse the text: adds amount + reason and type if amount and reason in the raw text
    tempDict = parseText(rawText, update.message.chat.username)

    # Feeding the missing elements in context.user_data
    if tempDict['amount'] != None:
        context.user_data['amount'] = tempDict['amount']

    if tempDict['reason'] != None:
        context.user_data['reason'] = tempDict['reason']
        context.user_data['typex'] = tempDict['typex']
    
    # Add the telegram handle to context.user_dat
    context.user_data['user'] = update.message.chat.username

    # Add the wbs to context.user_data
    try: 
       #context.user_data['wbs'] = db.get_wbs(context.user_data['user'])
       context.user_data['wbs'] = '000001'

    except KeyError:
        update.message.reply_text("I don't have a wbs yet. Please type '/wbs yourWbsHere' to be able to record business expenses. Then you'll have to record this expense again.")
    except Exception as e:
        logger.error('Problem while trying to recover the wbs from the database. Error: %s', e)
    

    isComplete = checkCompletion(context.user_data)
    if isComplete:
        logger.info('Expense data is complete. Ready for database injection.')
        expId = injectData(context.user_data)
        update.message.reply_text('''Thanks, I have recorded your expense correctly.''')
        context.user_data.clear()

##########################################################################################################
# Starting the bot
##########################################################################################################

#Initiating the classes
logger.info('Initialising the classes')

db = DBHelper()
db.setup()

#Starting the bot
logger.info('Starting the bot')

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

#Initiate the "start" conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states = {EMAIL: [MessageHandler(Filters.text, email)],
        CURRENCY: [MessageHandler(Filters.text, currency)],
        },
    fallbacks=[CommandHandler('stopit', stopit)]
    )

#Registering handlers

dispatcher.add_handler(conv_handler)
dispatcher.add_handler(CommandHandler('help', helpmsg))
dispatcher.add_handler(CommandHandler('status', status))
dispatcher.add_handler(CommandHandler('export', export))
dispatcher.add_handler(CommandHandler('email', emailCheck,pass_args=True))

dispatcher.add_handler(MessageHandler(Filters.caption, textCapture))
dispatcher.add_handler(MessageHandler(Filters.photo | Filters.document, photoCapture))
dispatcher.add_handler(MessageHandler(Filters.text, textCapture))

#Initiate the job_queue performed by the server. The job looks 
# for pending expenses then logs these into IQ Navigator
#j = JobQueue()
#j.set_dispatcher(dispatcher)
#jobTime = datetime.timedelta(minutes=30)
#job_logExpenses = j.run_repeating(iqnExpensesLog,jobTime)
#j.start()

#Starting the server
logger.info('Starting the server')
updater.start_webhook(listen='0.0.0.0',
                      port=443,
                      key='/var/www/expenseBot/ssl/PRODPRIVATE.key',
                      cert='/var/www/expenseBot/ssl/PRODPUBLIC.pem',
                      webhook_url='https://prod.expensebot.design/',
                      )
logger.info('Server started')

