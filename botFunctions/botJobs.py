import telegram
from telegram.ext import CallbackContext
from botFunctions.iqnCommands import *
from botClasses.classes import *
import os
#from logger.logger import logger

db = DBHelper()
 
def iqnExpensesLog(context: telegram.ext.CallbackContext):
    """
    Logs all pending expenses into IQ Navigator.

    """

    activeUsers = db.get_users_by_status('active')
    
    driver = initiateDriver()

    #For each active user, perform the same loop
    for user in activeUsers:

        #Extract all pending expenses 
        expenses = db.extract_expenses(user[0], 'pending')

        #If the current user has pending expenses, then proceed. If not, close driver.
        if expenses:
        
            logger.info('Number of pending expenses found: %s', len(expenses))
            logger.info('Expenses for %s', user[0])
            #Create the expense objects list
            pd = createExpensesList(user[0])
            
            try:
                driver = login(driver, user[1], user[2])
                result = checkExpenseReport(driver)
                driver = result[0]

                #If there is no expense report, create one - result[1] boolean is False,
                if not result[1]:
                    driver = createExpenseReport(driver)

                driver = addExpense(driver, pd)
                driver = saveExpenseReport(driver)
                #db.updateStatus('pending','logged',user[0])
                #print('Expenses successfully logged')
        
            except Exception as e:
                logger.error('Could not perform iqnExpenseLog job. Error: %s', e) 

    driver.quit()
    



def submitJob(activeUser):
    """
    Submits the latest expense report for approval.
    """
    
    #Get the credentials for current user
    user = db.get_credentials(activeUser)

    #Start the navigation on Chrome
#    driver = initiateDriver()
#
#    try:
#        driver = login(driver, user[0], user[1])
#    except Exception as e:
#        logger.error('Cannot login to IQ Navigator. User: %s. Error: %s', activeUser, e)
#
#
#    result = checkExpenseReport(driver)
#    driver = result[0]
#
#
#    try:
#        driver = submitExpenseReport(driver) 
#        successSubmit = True
#    except Exception as e:
#        logger.error('Could not submit the current time report for user %s. Error: %s', activeUser, e)
#        successSubmit = False
#    driver.quit()

    #Update all logged expenses' status to "submitted"
    db.updateStatus('logged','submitted',user[0])
    successSubmit = True        #This line for testing purposes only
    logger.info('Fake submit ok')

    return successSubmit

def testJob(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='467786379', text='Checking in')
