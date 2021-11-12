#coding: utf-8
from botClasses.classes import DBHelper
from botClasses.reportClass import ExpenseReport
from botFunctions.botLogic import toMarkdown, registeredEmail, totalPending 
from botParams import bot
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import telegram
import os
from logger.logger import logger
import time
import csv
from datetime import datetime
from maya import dateparser


# Database helpers
#################################################################

db = DBHelper()


#################################################################
# Decorators
#################################################################

def commandTrack(func):
    def wrapper(update, context):
       
        try:
            value = " ".join(context.args)
            #value = context.args[0]
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
    messages = ['''To record a new business expense, 
send the bot a picture of your receipt, with the amount and reason in the caption, separated by a comma (eg, "12, coffee with Johnny").
You can also record an expense in a different currency: follow the same procedure, just add the 3 letters of a currency after the amount (eg, "12 eur, lunch with Paul)''',
    f'Send a message to support@expensebot.net if you run into trouble or have questions about the bot.']
    for msg in messages:
        update.message.reply_text(msg)


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
    update.message.reply_text("Hey, welcome to expensebot.net! Before you can start recording business expenses, I will need to set you up." )
    message = (f"It will take 1 minute, but you can stop at any point by typing /stop. \n"
                "First, I need an email. I will use this email to send you the expense reports you request via the /export command.\n"
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
        keyboard = [['EUR','RUB','USD'],
                ['NZD','AUD','UAH']]
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

        ###########################################################################

        try:
            db.add_user(telegramUsername, email, currency)
            time.sleep(1)
            update.message.reply_text('Congrats, you are now all set!')
        except Exception as e:
            logger.error(f'User {telegramUsername} could not be created', e)
            update.message.reply_text(f'It seems I ran into trouble. Please start again in a while using the /start commend. Apologies :/')
            ConversationHandler.END

        #Creating a specific folder to save user's receipts
        try:
            path = '/var/www/expenseBot/receipts/' + telegramUsername
            os.mkdir(path)
            path = '/var/www/expenseBot/exports/' + telegramUsername
            os.mkdir(path)
        except:
            logger.error('Error when creating user\'s folder. User: %s', telegramUsername)
            ConversationHandler.END
 
        logger.info('Adding user %s to the users database', telegramUsername)

    return ConversationHandler.END

@commandTrack
def stopit(update, context):
    update.message.reply_text("I am stopping now")

@commandTrack
def export(update, context):

    user = update.message.chat.username
    email = db.get_user_email(user)

    if len(context.args) >= 1:
        
        #Create and parse a date with all parameters after the /export command
        date_exp = ' '.join(context.args)
        date_exp = dateparser.parse(date_exp) 

        responseBack = f'I have exported your expenses from {date_exp.strftime("%A, %B %-d")} and sent them to your email, {email}'
    else:
        responseBack = f'I have exported all of your expenses to your email, {email}'
        date_exp = None

    report = ExpenseReport(user)
    report.getExpenses('expenses.sqlite', date_exp)
    report.generateXls()
    report.receiptZip()

    result = report.sendMail(email)    
    #Sending the email
    
    if result != 202:
        update.message.reply_text('oops, there\'s been a problem')
        logger.error(f'Email with expense export not sent. {result}')
    else:
        update.message.reply_text(responseBack)
    logger.info(f'Export sent to {user}')

@commandTrack
def last(update, context):
    #Extracting ALL pending expenses. We choose the "pending" status because it's the first one assigned to a new expense object.
    allExpenses = db.extract_expenses(update.message.chat.username, "pending")

    if len(context.args) >= 1:
        nbExpenses = int(context.args[0])
    else:
        nbExpenses = 5

    #Only keep the last 5 expenses
    if len(allExpenses) > 0:
        result = allExpenses[-nbExpenses:]
        #total = totalPending(result)
        result = toMarkdown(result)
        update.message.reply_text(result)
        #update.message.reply_text(f'Total for these expenses: {total}')
    
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