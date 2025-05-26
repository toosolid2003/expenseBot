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
from botFunctions.openai_func import *
import json
from dotenv import load_dotenv, dotenv_value

#################################################################
# Constants
#################################################################

#Regular expression to identify a new expense. Not used yet.
regex = r"[0-9]+[.]?[0-9]*[\s]?([a-zA-Z]{3})?[,.;:]{1}[\s*][a-zA-Z0-9]*"

#Parameters of the assistant
assistant_mood = '''You are a professionnal assistant, focused on getting users to record their expenses.
Users need to provide you with the expense amount, its currency and description, and a photo of a receipt.
The best is to provide all of it together, with the following syntax: amount currency, description. For instance: 
12 usd, restaurant with Johhny.'''

client = OpenAI(api_key=OPEN_AI)



#################################################################
# Input handlers
#################################################################

@inputTrack
def chat_with_ai(update, context):
    '''Sends the user input to an LLM for an answer. Responds to the user.'''

    logger.debug(f"Sending user input -{update.message.text}- to chatGPT for parsing.")
    assert isinstance(update.message.text, str), "question should be a string"


    # Step 1: See if the user has an intention to record an expense
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[{"role": "system", "content": assistant_mood},{"role": "user", "content": update.message.text }],
    tools=funcs,
    tool_choice={"type":"function", "function": {"name": "get_intent"}}
    )

    r = response.choices[0].message.tool_calls[0].function.arguments

    #Loading the string into json to turn it into a dic
    j = json.loads(r)


    # If the intent is to record an expense, then use another functon call to OpenAI to extract the data
    if j['intent'] == 'record expense' or j['intent'] == 'submit expense':
        res = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages = [{"role":"user","content":update.message.text}],
        tools=funcs,
        tool_choice={"type":"function", "function": {"name": "get_expense_data"}}
    )

        r = res.choices[0].message.tool_calls[0].function.arguments
        j = json.loads(r) 
        #Temporary print
        print(j)
    
        #Creates an expense object and stores it in context.user_data, if it does not exist yet.
        if 'expense' not in context.user_data.keys():
            context.user_data['expense'] = Expense(update.message.from_user.id) 
    
        #Inject the parsing results from OpenAI as a dict into the expense object
        context.user_data['expense'].get_input(j)
        print(context.user_data['expense'])
    
    else:
        response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[{"role": "system", "content": assistant_mood},{"role": "user", "content": update.message.text }],
    ) 
        text_response = response.choices[0].message.content
        update.message.reply_text(text_response)

def ai_text_handler(update, context):
    '''Handles the user inputs that dont match the regex'''

    #Get the text input, whether from the caption or the normal text field
    if update.message.text is not None:
        user_input = update.message.text
    elif update.message.caption is not None:
        user_input = update.message.caption
    else:
        logger.debug(f'No text or caption provided')

    #Is there any existing expense object? If not, create a new expense object
    if 'expense' not in context.user_data.keys():
        context.user_data['expense'] = Expense(update.message.from_user.id) 
        logger.debug(f"Created a new expense object")

    #Extract the data from the user input
    res = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages = [{"role":"user","content":user_input}],
        tools=funcs,
        tool_choice={"type":"function", "function": {"name": "get_expense_data"}}
    )

    r = res.choices[0].message.tool_calls[0].function.arguments
    j = json.loads(r) 
    logger.debug(f'Extracted data: {j}')

    #Add the extracted data to the expense object
    context.user_data['expense'].get_input(j)

    #Check if the expense object has all the data it needs.
    context.user_data['expense'].check_if_complete()
    logger.debug(f"Expense: {context.user_data['expense']}")

    #If not, respond to user with the missing data points that he/she needs to provide

def totalHandler(update, context):

    logger.debug(f"Manually parsing input for {update.message.from_user.id}.")
    
    #Initiating the parser
    p = Parser()
    ##Parsing the user input
    if update.message.caption:
        logger.debug(f'Caption detected')
        p.parse_text(update.message.caption)
        
        try:
            p.parse_picture(update.message.document['file_id'],update.message.from_user.id, bot)
        except TypeError:
            p.parse_picture(update.message.photo[-1]['file_id'],update.message.from_user.id, bot)    
    elif update.message.text:
        p.parse_text(update.message.text)
    else:
        try:
            p.parse_picture(update.message.document['file_id'],update.message.from_user.id, bot)
        except TypeError:
            p.parse_picture(update.message.photo[-1]['file_id'],update.message.from_user.id, bot)    

    #Creates an expense object and stores it in context.user_data, if it does not exist yet.
    if 'expense' not in context.user_data.keys():
        context.user_data['expense'] = Expense(update.message.from_user.id) 
        logger.debug(f"Created a new expense object")

    
    #Storing the parsing results in the expense object

    logger.debug(f'Parsed input: {p.result}')
    logger.debug(f'Assigning the parsed data to the expense object')
    context.user_data['expense'].get_input(p.result)

    #Testing if expense is complete. If it is complete, it has been
    #automatically saved to the database and the 'complete' flag is True.
    #We just need to delete it. 

    context.user_data['expense'].check_if_complete()
    if context.user_data['expense'].complete:
        update.message.reply_text("Thanks, I have recorded your expense!. \nFeel free to check your latest expenses using the /last command!")
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



updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = Bot(token=BOT_TOKEN)

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

dispatcher.add_handler(MessageHandler(Filters.document, totalHandler))
dispatcher.add_handler(MessageHandler(Filters.photo, totalHandler))
dispatcher.add_handler(MessageHandler(Filters.text and Filters.regex(regex), totalHandler))
dispatcher.add_handler(MessageHandler(Filters.text, ai_text_handler))

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

