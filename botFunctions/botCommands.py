#coding: utf-8
from botClasses.classes import DBHelper
from botFunctions.botLogic import toMarkdown, totalPending
from botFunctions.iqnCommands import wbsCheck
from botFunctions.botJobs import submitJob
from botFunctions.export_mail import sendExport
from botParams import bot
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import telegram
import os
from logger.logger import logger
import time

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

def inputTrack(func):
    def wrapper(update, context):

        if update.message.text:
            value = update.message.text
        elif update.message.caption:
            value = update.message.caption
        else:
            value = '' 

        db.add_datapoint(update.message.chat.username, func.__name__, value)
        return func(update, context)
    return wrapper



#################################################################
# Commands
#################################################################



@commandTrack
def helpmsg(update, context):
    text = '''To record an expense, just type in the amount, a curreny, a reason and attach a picture or document as receipt.
    Example: "19 usd, hotel California" -> hit send then just share a picture of the receipt with the bot'''
    update.message.reply_text(text)


#Conversation commands
#################################################################

# First Sign up process

#EMAIL, IQUSERNAME, IQPASSWORD, CURRENCY, WBS = range(5)
EMAIL, CURRENCY = range(2)


@commandTrack
def start(update, context):
    """Handles the setup process"""

    #Checking if user exists
    userExists = db.checkExistingUser(update.message.chat.username)
    if userExists:
        update.message.reply_text('Hey, it looks like you already have an account with us. You are good to log your expenses.')
        return ConversationHandler.END

    #If user does not exist yet, proceed.
    update.message.reply_text("Hey, welcome to the Expense Bot. Before you can start recording business expenses, I will need to set you up." )
    message = (f"It will take 1 minute, but you can stop at any point by typing /stop. \n"
                "First, I need an email. I will use this email to send you the expense reports you request via /export.\n"
                "Ok. What email should I use?")
    update.message.reply_text(message)
    return EMAIL


@commandTrack
def email(update, context):
    """Verifying the email given to the bot""" 

    email = update.message.text
    if '/stop' in email:
        update.message.reply_text('OK then. Feel free to resume the sign up by typing "/start" when you are ready')
        return ConversationHandler.END
    else:
        #Check with web database if the email is registered?
        update.message.reply_text('Thanks for your email, {}.'.format(email))
        context.user_data['email'] = email
        update.message.reply_text('Now, what currency should I use to record your expenses?')
        keyboard = [['EUR','CHF','USD'],
                ['NZD','AUD','CAD']]
        reply = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        bot.send_message(chat_id=update.message.chat.id, reply_markup=reply, text='Choose among the following:')
        #Remove the custome keyboard used in password state
        telegram.ReplyKeyboardRemove()

    return CURRENCY

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
        update.message.reply_text('Thanks for that. Now, let me add you to our list of users.')

        #Adding the new user to the users database now
        telegramUsername = update.message.chat.username
        email = context.user_data['email']
        currency = context.user_data['currency']

        #Fake data to make sure the add_user function does not raise an exception
        wbs = '000000'
        iq_username = 'rando'
        iq_password = 'rando'
        ###########################################################################

        logger.info('Adding user %s to the users database', telegramUsername)
        db.add_user(telegramUsername, iq_username, iq_password, email, wbs, currency)
        time.sleep(1)
        update.message.reply_text('Congrats, you are now all set!')

        #Creating a specific folder to save user's receipts
        try:
            path = '/var/www/expenseBot/receipts/' + telegramUsername
            os.mkdir(path)
            path = '/var/www/expenseBot/exports/' + telegramUsername
            os.mkdir(path)
        except:
            logger.error('Error when creating user\'s folder. User: %s', telegramUsername)
 

    return ConversationHandler.END

@commandTrack
def stopit(update, context):
    update.message.reply_text("I am stopping now")

@commandTrack
def export(update, context):
    filename = db.extract_all(update.message.chat.username)
    email = db.get_user_email(update.message.chat.username)
    response = sendExport('support@expensebot.net', email, filename)
    if response.status_code != 202:
        update.message.reply_text('oops, there\'s been a problem')
        logger.error(f'Email with expense export not sent. {response.status_code}')

    update.message.reply_text(f'I have exported all your expenses in a csv file and ' 
    f'sent it to your email: {email}.')

@commandTrack
def status(update, context):
    #Extracting ALL pending expenses. We choose the "pending" status because it's the first one assigned to a new expense object.
    allExpenses = db.extract_expenses(update.message.chat.username, "pending")

    #Only keep the last 5 expenses
    if len(allExpenses) > 0:
        result = allExpenses[-5:]
        total = totalPending(result)
        result = toMarkdown(result)
        update.message.reply_text(result)
        update.message.reply_text(f'Total for these expenses: {total}')
    
    else:
        update.message.reply_text(f"I'm sorry, there is no pending expense for you :/")

@commandTrack
def emailCheck(update, context):
    """Check and update the user's email address."""

    if len(context.args) == 1:
        try:
            db.update_user_email(update.message.chat.username, context.args[0])
        except Exception as e:
            logger.info(e)

        update.message.reply_text(f'I have updated your email, thanks!')
    else:
        userEmail = db.get_user_email(update.message.chat.username)
        update.message.reply_text('Your current email address is {}'.format(userEmail))
        update.message.reply_text('Type /email followed by your new email address to update it.')