from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, JobQueue, CallbackContext
from telegram import Bot
from botClasses.classes import DBHelper
from botClasses.parserClass import Parser
from botClasses.expenseClass import Expense
from botFunctions.botCommands import *
from botFunctions.botLogic import *
from logger.logger import logger
from botParams import *
import re
from openai import OpenAI, api_key

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
def chat_with_ai(update, context):
    '''Sends the user input to an LLM for an answer. Responds to the user.'''

    update.message.reply_text("Asking chatGPT for help!")
    assert isinstance(update.message.text, str), "question should be a string"

    #Parameters of the assistant
    assistant_mood = "You are a professionnal assistant, focused on getting users to submit their expenses"
    client = OpenAI(api_key='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')

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": assistant_mood},
    {"role": "user", "content": update.message.text }],
    temperature=0.5,
    max_tokens=256
    )

    result = response.choices[0].message.content
    update.message.reply_text(result)


def totalHandler(update, context):

    update.message.reply_text("Saving your expense")
    
    #Initiating the parser
    p = Parser()
    ##Parsing the user input
    if update.message.caption:
        p.parse_text(update.message.caption)
        p.parse_picture(update.message.photo[-1]['file_id'],update.message.chat.username, bot)
    elif update.message.text:
        p.parse_text(update.message.text)
    else:
        p.parse_picture(update.message.photo[-1]['file_id'],update.message.chat.username, bot) 
    

    #Creates an expense object and stores it in context.user_data, if it does not exist yet.
    if 'expense' not in context.user_data.keys():
        context.user_data['expense'] = Expense(update.message.chat.username) 

    
    #Storing the parsing results in the expense object
    logger.debug(f'Parsed input: {p.result}')
    logger.debug(f'Assigning the parsed data to the expense object')
    context.user_data['expense'].get_input(p.result)

    #Testing if expense is complete. If it is complete, it has been
    #automatically saved to the database and the 'complete' flag is True.
    #We just need to delete it. 

    if context.user_data['expense'].complete:
        del context.user_data['expense']
        logger.debug(f'Expense complete. Deleted now.')






##########################################################################################################
# Starting the bot
##########################################################################################################

#Initiating the classes
# logger.info('Initialising the classes')

# db = DBHelper()
# db.setup()

#Starting the bot
logger.info('Starting the bot')

with open('bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = Bot(token=TOKEN)

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
dispatcher.add_handler(CommandHandler('last', last))
dispatcher.add_handler(CommandHandler('export', export))
dispatcher.add_handler(CommandHandler('email', emailCheck,pass_args=True))

dispatcher.add_handler(MessageHandler(Filters.document and Filters.caption, totalHandler))
dispatcher.add_handler(MessageHandler(Filters.photo, totalHandler))
dispatcher.add_handler(MessageHandler(Filters.text and Filters.regex(regex), totalHandler))
dispatcher.add_handler(MessageHandler(Filters.text, chat_with_ai))

#Starting the server
# logger.info('Starting the server')
# updater.start_webhook(listen='0.0.0.0',
#                       port=443,
#                       key= KEY,
#                       cert= CERT,
#                       webhook_url=WEBHOOK,
#                       )
# logger.info('Server started')
updater.start_polling()

