#coding: utf-8
from botClasses.classes import *
from botFunctions.botLogic import toMarkdown, totalPending
from botFunctions.iqnCommands import wbsCheck
from botFunctions.botJobs import submitJob
from botParams import bot
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import telegram
import os
from logger.logger import logger

# Database helpers
#################################################################

db = DBHelper()


#################################################################
# Decorators
#################################################################

def commandTrack(func):
    def wrapper(update, context):
       
        try:
            value = context.args[0]
        except:
            value = ''

        db.add_datapoint(update.message.chat.username, func.__name__, value)
        return func(update, context)
    return wrapper



#################################################################
# Commands
#################################################################

@commandTrack
def wbs(update, context):
    '''Changes the wbs value if it is provided as a parameter
    Otherwise, displays the current WBS against which expenses are logged'''


    
    if len(context.args) > 0:
        newWBS = context.args[0].upper()
        db.update_wbs(update.message.chat.username, newWBS)

        wbs = db.get_wbs(update.message.chat.username)
        update.message.reply_text('Your new WBS for expenses: {}'.format(wbs))


        #Check if the wbs is valid
        isWbsValid = wbsCheck(update.message.chat.username, wbs)
        if not isWbsValid:
            update.message.reply_text('There is a little problem with this wbs. Whether you are not allowed to use it or maybe the code is invalid, but it does not seem to be working for you. Try to update it again or just reach out to your manager to make sure you can use it.')
    else:
        try:
            wbs = db.get_wbs(update.message.chat.username)
            update.message.reply_text('Your current WBS for expenses is {}'.format(wbs))
        except:
            update.message.reply_text("You don't have a WBS assigned yet. Please type '/wbs xxxx' (xxxx being your wbs number) to be able to record your business expenses.")


@commandTrack
def submit(update, context):
    '''Submit into IQ Navigtor the expenses that are still in pending status'''
    
    result = True
    result = submitJob(update.message.chat.username)
    if result:
        update.message.reply_text('Alright, your expenses have been submitted for approval')
        db.updateStatus('logged','submitted', update.message.chat.username)
    else:
        update.message.reply_text('The submission seems to have failed. I won\'t be able to help from here, so I suggest you have a look on IQ Navigator to sort it out.')


@commandTrack
def helpmsg(update, context):
    text = '''To log an expense, send me an amount (number), a reason (text) and a receipt (a picture or document). 
I have other talents too, just type '/' to display my available commands. Enjoy!'''
    update.message.reply_text(text)


@commandTrack
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

def iqn(update, context):
    '''Update IQ Navigator credentials'''
    iq_username = context.args[0]
    iq_password = context.args[1]

    db.update_iq_creds(update.message.chat.username, iq_username, iq_password)     
    update.message.reply_text('Your IQ Navigator credentials have been updated. Thanks!')

#Conversation commands
#################################################################

# First Sign up process

#EMAIL, IQUSERNAME, IQPASSWORD, CURRENCY, WBS = range(5)
EMAIL, CURRENCY, WBS = range(3)


@commandTrack
def start(update, context):
    """Handles the setup process"""
    update.message.reply_text("Hey, welcome to the Expense Bot. Before you can start recoding business expenses, I will need fo finish the sign-up process with you. If you have not registsred yet, have a look on our website (www.expensebot.net/signup). ")
    update.message.reply_text("It will take 1 min, but you can stop at any point by typing '/stop'. Let's start! Can you confirm the email address you want to use?")
    update.message.reply_text(f'Chat id: {update.message.chat.id}')
    return EMAIL


@commandTrack
def email(update, context):
    """Verifying the email given to the bot with a list of registered emails in the web"""

    email = update.message.text
    if '/stop' in email:
        update.message.reply_text('OK then. Feel free to resume the sign up by typing "/start" when you are ready')
        return ConversationHandler.END
    else:
        #Check with web database if the email is registered
        update.message.reply_text('Thanks for your email, {}, and welcome back.'.format(email))
        context.user_data['email'] = email
        update.message.reply_text('Now, what currency should I use to record your expenses?')
        keyboard = [['EUR','CHF','USD'],
                ['NZD','AUD','CAD']]
        reply = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.send_message(chat_id=update.message.chat.id, reply_markup=reply, text='Choose among the following:')
        #Remove the custome keyboard used in password state
        telegram.ReplyKeyboardRemove()

    return CURRENCY




#@commandTrack
#def iqusername(update, context):
#    """Gimme your IQ username"""
#    username = update.message.text
#
#    if '/stop' in username:
#        update.message.reply_text("Let's stop then. Remember: I will still need at least a wbs to start recording your business expenses. \nYou can send it to me using the '/wbs' command. For instance, '/wbs yourWbsHere'.")
#        return ConversationHandler.END
#    else:
#        context.user_data['iq_username'] = username
#        update.message.reply_text('Thanks for your username. What would your password be?')
#
#    return IQPASSWORD
#
#
#
#@commandTrack
#def iqpassword(update, context):
#    """Gimme your password"""
#
#    context.user_data['password'] = update.message.text
#    if '/stop' in context.user_data['password']:
#        update.message.reply_text("Ok, let's stop here. You can restart the process anytime by typing '/start'.")
#        return ConversationHandler.END
#
#    else:
#        update.message.reply_text('Thanks. Now, what currency should I use to record your expenses?')
#        keyboard = [['EUR','CHF','USD'],
#                ['NZD','AUD','CAD']]
#        reply = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
#        bot.send_message(chat_id=update.message.chat.id, reply_markup=reply, text='Choose among the following:')
#
#    return CURRENCY
#

@commandTrack
def currency(update, context):
    """
    Captures the preferred currency of the user.
    """

    
    if '/stop' in update.message.text:
        update.message.reply_text("Ok, let's stop here. You can restart the process anytime by typing '/start'.")
        return ConversationHandler.END

    else:
        context.user_data['currency'] = update.message.text
        update.message.reply_text('Thanks for that. Last thing: I need a wbs to start recording your expenses. It is not definitive, you can always change it by using the "/wbs" command. Ok, what is your current WBS?')

    return WBS


@commandTrack
def wbsSetup(update, context):
    """Captures a WBS code and records the data in the users table"""

    wbs = update.message.text

    if '/stop' in wbs:
        update.message.reply_text("No worrie, let's stop here. You will need to send me a wbs though, otherwise I won't be able to record your business expenses. You can add or change the current wbs using the /wbs command.")
    else:
        #Adding the new user to the users database now
        telegramUsername = update.message.chat.username
        #iq_username = context.user_data['iq_username']
        #iq_password = context.user_data['password']
        email = context.user_data['email']
        currency = context.user_data['currency']

        
        logger.info('Adding user %s to the users database', telegramUsername)
       # db.add_user(telegramUsername, iq_username, iq_password, email, wbs, currency)
        update.message.reply_text('Thanks for the WBS ({}), and congrats, you are now all set!'.format(wbs))
        #Creating a specific folder to save user's receipts
        try:
            path = '/var/www/expenseBot/receipts/' + telegramUsername
            os.mkdir(path)
        except:
            logger.error('Error when creating user\'s folder. User: %s', telegramUsername)
 

       
        #Checking the validity of the WBS
        isWbsValid = wbsCheck(update.message.chat.username, wbs)

        if not isWbsValid:
            update.message.reply_text('Your WBS does not seem to be working for you. Make sure it is activated before I can record any expense for you! Check this with your manager, maybe? \nPlease use the /wbs command if you need to change your wbs.')


    return ConversationHandler.END


@commandTrack
def stopit(update, context):
    update.message.reply_text('Ok, I stop now')

    return ConversationHandler.END


