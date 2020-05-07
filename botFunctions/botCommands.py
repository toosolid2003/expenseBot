#coding: utf-8
from botClasses.classes import *
from botFunctions.botLogic import toMarkdown, totalPending
from botFunctions.iqnCommands import wbsCheck
from botParams import bot
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import telegram
import os

# Database helpers
#################################################################

userdb = userDB()
db = DBHelper()

# Commands
#################################################################

def wbs(update, context):
    '''Changes the wbs value if it is provided as a parameter
    Otherwise, displays the current WBS against which expenses are logged'''


    
    if len(context.args) > 0:
        userdb.update_wbs(update.message.chat.username, context.args[0])

        wbs = userdb.get_wbs(update.message.chat.username)
        update.message.reply_text('Your new WBS: {}'.format(wbs))

        #Check if the wbs is valid
        isWbsValid = wbsCheck(update.message.chat.username, wbs)
        if not isWbsValid:
            update.message.reply_text('There is a little problem with this wbs. Whether you are not allowed to use it or maybe the code is invalid, but it does not seem to be working for you. Try to update it again or just reach out to your manager to make sure you can use it.')
    else:
        try:
            wbs = userdb.get_wbs(update.message.chat.username)
            update.message.reply_text('Your current WBS is {}'.format(wbs))
        except:
            update.message.reply_text("You don't have a WBS assigned yet. Please type '/wbs xxxx' (xxxx being your wbs number) to be able to record your business expenses.")



def submit(update, context):
    '''Submit into IQ Navigtor the expenses that are still in pending status'''

    response = submit_expenses(update.message.chat.username)
    update.message.reply_text(response)

def helpmsg(update, context):
    text = '''To log an expense, send me an amount (number), a reason (text) and a receipt (a picture or document). 
I have other talents too, just type '/' to display my available commands. Enjoy!'''
    update.message.reply_text(text)

def status(update, context):
    '''Returns a list of pending expenses for current Telegram user'''
    
    currentExpenses = db.extract_expenses(update.message.chat.username, 'logged')
    currentExpenses += db.extract_expenses(update.message.chat.username, 'pending')

    if currentExpenses:
        text = 'Here are the expenses that I have recorded for you:\n\n'
        text += toMarkdown(currentExpenses)
        text += '\n Total: {} CHF'.format(totalPending(currentExpenses))
        update.message.reply_text(text)

    else:
        update.message.reply_text('I don\'t have any expenses for you. They must all be in IQ Navigator already :)')

#Conversation commands
#################################################################

EMAIL, IQUSERNAME, IQPASSWORD, CURRENCY, WBS = range(5)

def start(update, context):
    """Handles the setup process"""
    update.message.reply_text("""Hey, welcome to the Expense Bot. Before you can start recoding business expenses with me, I will need to collect some information about you (email, iq navigator credentials, wbs).
It will take 5 min at most, but you can stop at any point by typing '/stop'.""")
    update.message.reply_text("Let's start! What email address do you want to use?")

    return EMAIL

def email(update, context):
    """Gimme your email"""

    email = update.message.text
    if '/stop' in email:
        update.message.reply_text('OK then. Feel free to resume the sign up by typing "/start" when you are ready')
        return ConversationHandler.END
    else:
        update.message.reply_text('Thanks for your email ({}). Now, can you give me the username you use with IQ Navigator?'.format(email))
        context.user_data['email'] = email

        return IQUSERNAME



def iqusername(update, context):
    """Gimme your IQ username"""
    username = update.message.text

    if '/stop' in username:
        update.message.reply_text("Let's stop then. Remember: I will still need at least a wbs to start recording your business expenses. \nYou can send it to me using the '/wbs' command. For instance, '/wbs yourWbsHere'.")
        return ConversationHandler.END
    else:
        context.user_data['iq_username'] = username
        update.message.reply_text('Thanks for your username. What would your password be?')

    return IQPASSWORD



def iqpassword(update, context):
    """Gimme your password"""

    context.user_data['password'] = update.message.text
    if '/stop' in context.user_data['password']:
        update.message.reply_text("Ok, let's stop here. You can restart the process anytime by typing '/start'.")
        return ConversationHandler.END

    else:
        update.message.reply_text('Thanks. Now, what would be your preferred currency for me to use?')
        keyboard = [['EUR','CHF','USD'],
                ['NZD','AUD','CAD']]
        reply = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.send_message(chat_id=update.message.chat.id, reply_markup=reply, text='Choose your currency:')

    return CURRENCY

def currency(update, context):
    """
    Captures the preferred currency of the user.
    """

    if '/stop' in update.message.text:
        update.message.reply_text("Ok, let's stop here. You can restart the process anytime by typing '/start'.")
        return ConversationHandler.END

    else:
        context.user_data['currency'] = update.message.text
        update.message.reply_text('Thanks for that. Last thing: I need a wbs to start recording your expenses. It is not definitive, you can always change it by using the "/wbs" command. Ok, what would this first WBS be?')

    return WBS

def wbsSetup(update, context):
    """Gimme a wbs"""

    wbs = update.message.text

    if '/stop' in wbs:
        update.message.reply_text("No worrie, let's stop here. You will need to send me a wbs though, otherwise I won't be able to record your business expenses. You can add or change the current wbs by typing:\n '/wbs xxxxxx'.")
    else:
        #Adding the new user to the users database now
        db = userDB()
        db.setup()
        telegramUsername = update.message.chat.username
        iq_username = context.user_data['iq_username']
        iq_password = context.user_data['password']
        email = context.user_data['email']
        currency = context.user_data['currency']
        try:
            db.add_user(telegramUsername, iq_username, iq_password, email, wbs, currency)
            update.message.reply_text('Thanks for the WBS ({}), and congrats, you are now all set!'.format(wbs))
        except Exception as e:
            print('Adding user failed')
            print(e)


        #Creating a specific folder to save user's receipts
        try:
            path = '/var/www/expenseBot/receipts/' + telegramUsername
            os.mkdir(path)
        except:
            print('Error when creating user\'s folder')
        
        #Checking the validity of the WBS
        isWbsValid = wbsCheck(update.message.chat.username, wbs)

        if not isWbsValid:
            update.message.reply_text('Your WBS does not seem to be working for you. Make sure it is activated before I can record any expense for you! Check this with your manager, maybe? \nPlease use the /wbs command if you need to change your wbs.')


    return ConversationHandler.END

def stopit(update, context):
    update.message.reply_text('Ok, I stop now')

    return ConversationHandler.END


