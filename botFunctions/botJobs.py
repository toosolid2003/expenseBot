import telegram
from telegram.ext import CallbackContext
from botFunctions.iqnCommands import *
from botClasses.classes import DBHelper

def iqnExpensesLog(context: telegram.ext.CallbackContext):
    """Logs all pending expenses into IQ Navigator.

    Input: telegram handle (future)

    """

    db = DBHelper()
    res = db.extract_pending('thedropper')
    if res:
        try:
            driver = login('tsegura2','Brutasse1-')
            driver = createExpenseReport(driver)
            pd = createExpensesList('thedropper')
            driver = addExpense(driver, pd)
            driver = saveExpenseReport(driver)
            db.updateStatus('pending','logged','thedropper')
            print('Expenses successfully logged')
    
        except Exception as e:
            print('Something went wrong: \n')
            print(e)

def testJob(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='467786379', text='Checking in')
