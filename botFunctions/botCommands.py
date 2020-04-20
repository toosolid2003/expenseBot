#coding: utf8
from botClasses.classes import *
from botFunctions.botLogic import toMarkdown, totalPending
# Commands
#################################################################

def start(update, context):
    text = '''Hello there, I'm expenseBot. My sole purpose: making business expenses easy for you to log and track.
No one wants to waste time doing that, so here I am. Type '/help' if you want to know what I can do for you.'''
    update.message.reply_text(text)

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

def setUp(update, context):
    '''Takes the username and password of a new user'''

    update.message.reply_text('Coming soon...')
#    if len(context.args) > 0:
#        username = context.args[0]
#        password = context.args[1]
#        dbuser = userDB()
#        dbuser.add_user(update.message.chat.username, username, password)
#        update.message.reply_text('Thanks, I have username: {} and password: {}'.format(username, password))
#    else:
#        update.message.reply_text('Sorry, I did not understand. Make sure you separate the command, the username and the password by a space for me to understand which is which. Eg: /setup myusername mypassword')
#
def status(update, context):
    '''Returns a list of pending expenses for current Telegram user'''

    text = 'Here are the expenses that you recorded:\n\n'
    text += toMarkdown(update.message.chat.username)
    total = totalPending(update.message.chat.username)
    text += '\n Total: {} CHF'.format(total)
    update.message.reply_text(text)

