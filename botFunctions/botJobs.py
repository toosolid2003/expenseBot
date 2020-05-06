import telegram
from telegram.ext import CallbackContext
from botFunctions.iqnCommands import *
from botClasses.classes import *
import os

db = DBHelper()
userdb = userDB()
 
def iqnExpensesLog(context: telegram.ext.CallbackContext):
    """
    Logs all pending expenses into IQ Navigator.

    """

    activeUsers = userdb.get_users_by_status('active')
    
    driver = initiateDriver()

    #For each active user, perform the same loop
    for user in activeUsers:

        #Extract all pending expenses 
        expenses = db.extract_expenses(user[0], 'pending')
        
        #If the current user has pending expenses, then proceed. If not, close driver.
        if expenses:

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
                db.updateStatus('pending','logged',user[0])
                print('Expenses successfully logged')
        
            except Exception as e:
                print('Something went wrong: \n')
                print(e)

    driver.quit()
    
    #Clean the system of the chromedriver processes
    os.system('pkill -f chrome')
def testJob(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='467786379', text='Checking in')
