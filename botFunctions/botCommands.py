#coding: utf8
from botClasses.classes import *
from botFunctions.botLogic import toMarkdown, totalPending
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

# Commands
#################################################################

def wbs(update, context):
    '''Changes the wbs value if it is provided as a parameter
    Otherwise, displays the current WBS against which expenses are logged'''
    #global WBS

    if len(context.args) > 0:
        context.user_data['wbs'] = context.args[0]
        update.message.reply_text('Your new WBS: {}'.format(context.user_data['wbs']))
    else:
        update.message.reply_text('Your current WBS is {}'.format(context.user_data['wbs']))

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

    text = 'Here are the expenses that you recorded:\n\n'
    text += toMarkdown(update.message.chat.username)
    total = totalPending(update.message.chat.username)
    text += '\n Total: {} CHF'.format(total)
    update.message.reply_text(text)

#Conversation commands
#################################################################

EMAIL, IQUSERNAME, IQPASSWORD, WBS = range(4)

def start(update, context):
    """Handles the setup process"""
    update.message.reply_text("""Hey, welcome to the Expense Bot. Before you can start recoding business expenses with me,I will need to collect some information about you (email, iq navigator credentials, wbs).

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
        update.message.reply_text('Thanks for your username. What would your password be?')

    return IQPASSWORD
def iqpassword(update, context):
    """Gimme your password"""

    password = update.message.text
    if '/stop' in password:
        update.message.reply_text("Ok, let's stop here. You can restart the process anytime by typing '/start'.")
        return ConversationHandler.END

    else:
        update.message.reply_text('Thanks for that. Last thing: I need a wbs to start recording your expenses. It is not definitive, you can always change it by using the "/wbs" command. Ok, what would this first WBS be?')

    return WBS

def wbsSetup(update, context):
    """Gimme a wbs"""

    wbs = update.message.text

    if '/stop' in wbs:
        update.message.reply_text("No worrie, let's stop here. You will need to send me a wbs though, otherwise I won't be able to record your business expenses. You can add or change the current wbs by typing:\n '/wbs yourNewWbsHere'.")
    else:
        context.user_data['wbs'] = wbs
        update.message.reply_text('Thanks for the WBS ({}), and congrats, you are now all set!'.format(context.user_data['wbs']))

    return ConversationHandler.END

def stopit(update, context):
    update.message.reply_text('Ok, I stop now')

    return ConversationHandler.END


