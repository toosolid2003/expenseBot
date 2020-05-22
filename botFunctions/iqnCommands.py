#coding: utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
from botClasses.classes import *
#from logger.logger import logger

db = DBHelper()

def initiateDriver():

    """Initiates the Chrome driver for the session"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--window-size=1920,1080");
        chrome_options.add_argument("--start-maximized");
        driver = Chrome(options=chrome_options)

    except Exception as e:
        #logger.error('Could not initiate Chrome driver. Error: %s', e)
        pass

    return driver

def login(driver, username, password):

    #Login sequence
    ##logger.info('Opening the login page')
    try:    
        #logger.info('Logging in...')
        driver.get('https://augustus.iqnavigator.com/wicket/wicket/page?x=s89lP8StUfw')
        element = driver.find_element_by_id('username')
        element.send_keys(username)
        elemental = driver.find_element_by_id('password')
        elemental.send_keys(password)
        elemental.send_keys(Keys.RETURN)
        #Home page - wait for the logout element to load before doing anything
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'logoutLink')))
        #logger.info('Logged in')

    except Exception as e:
        #logger.error('Driver could not log into IQ Navigator. Error: %s',e)
        pass

    return driver

def checkExpenseReport(driver):
    """
    Checks for an existing expense report

    If expense report is found, clicks on 'Edit Expense Report' and returns the driver.
    If not, driver goes back to home page.
    
    Returns a tuple with the driver and a boolean
    """

    try:
        #logger.info('Checking if an expense report exists')
        bt = driver.find_element_by_link_text('Expense Reports')
        bt.click()
        time.sleep(2)
        try:
            #Select the first exepense report available
            editReport = driver.find_element_by_link_text('Edit Expense Report')
            editReport.click()
            exists = True
            #logger.info('Expense Report found')

            #Click on Add expense button
            #logger.info('Opening the Add Expense Form')
            bt = driver.find_elements_by_class_name('actionButtonLabel')
            bt[2].click()
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'entryFieldsContainer:fieldGroup:fields:2:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:select')))
            #time.sleep(5)
    
        except NoSuchElementException:
            #If driver cannot find an expense report, goes back to home page
            #logger.info('Expense Report not found. Back to Home.')
            home = driver.find_element_by_link_text('Home')
            home.click()
            exists = False


    except Exception as e:
        #logger.error('Could not perform checkExpenseReport. Error: %s', e)
        pass

    return driver, exists

def createExpenseReport(driver):
    """
    Create a new expense report in IQ Navigator.

    Input: browser (driver) positionned on IQN Home Page
    Output: browser (driver) with Add Expense form open

    """

    #logger.info('Creating a new expense report')
    bt = driver.find_element_by_link_text('Create Expense Report')
    bt.click()

    # Click on Create expense report from Assignment page
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'actionButtonLabel')))
    bt = driver.find_elements_by_class_name('actionButtonLabel')
    bt[0].click()
    time.sleep(5)

    #Enter a title for the Expense Report
    expReportTile = driver.find_element_by_name('expenseReportEditPanel:border:border:content:border_body:fieldGroup:repeater:1:fieldWLOT:textField')
    expReportTile.send_keys('Expenses starting from {}'.format(time.strftime('%x')))
    #logger.info('Expense Report title added')

    #Add expense button
    #logger.info('Opening the Add Expense form')
    bt = driver.find_elements_by_class_name('actionButtonLabel')
    bt[2].click()
    time.sleep(5)
    
    return driver


def addExpense(driver, expObjList):
    """
    Records a new expense in the Add Expense form.
    Input: browser (driver) with Add Expense form open, list of expense objets
    Output: browser (driver) after all expenses are recorded.

    """
    #Creating a dictionnary to host the names of the fields on the Add Expense form
    fields = {'date':'entryFieldsContainer:fieldGroup:fields:1:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textBox',
            'amount':'entryFieldsContainer:fieldGroup:fields:3:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField',
            'reason':'entryFieldsContainer:fieldGroup:fields:4:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField',
            'receipt':'entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileInput',
            'attachBtn':'entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileSubmit:container:container_body:button',
            'wbs':'entryFieldsContainer:fieldGroup:fields:7:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:sizingWrapper:textField:autocompleteField',
            'type':'entryFieldsContainer:fieldGroup:fields:2:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:select'}
    
    #Creating a list of expenses in error, for later verification
    expensesInError = []
    expensesSaved = []

    # Add Expense form - start of the loop
    j = 0

    ## Enter date
    for exp in expObjList:

#        #logger.info('Adding expense {}'.format(j))

        #Enter type (html select)
        #logger.info('Adding type: {}'.format(exp.typex))
        select_element = driver.find_element_by_name(fields['type'])
        select_object = Select(select_element)
#        select_object.select_by_visible_text(exp.typex)
        select_object.select_by_value(exp.typex)
        time.sleep(2)

        #Enter date of expense
        #logger.info('Adding date: {}'.format(exp.date))
        label = driver.find_element_by_name(fields['date'])
        label.clear()
        label.send_keys(exp.date)
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Enter Amount
        #logger.info('Adding amount: {}'.format(exp.amount))
        label = driver.find_element_by_name(fields['amount'])
        label.clear()
        label.send_keys(str(exp.amount))
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Enter reason
        #logger.info('Adding reason: {}'.format(exp.reason))
        label = driver.find_element_by_name(fields['reason'])
        label.clear()
        label.send_keys(exp.reason)
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Upload receipt
        #logger.info('Uploading receipt: {}'.format(exp.receipt))
        btn = driver.find_element_by_name(fields['receipt'])
        btn.send_keys(exp.receipt)
        time.sleep(2)

        #Click on 'Attach' button
        buttn = driver.find_element_by_name(fields['attachBtn'])
        buttn.click()
        time.sleep(4)  #Wait for receipt to load

        #Enter WBS
        #logger.info('Adding WBS: {}'.format(exp.wbs))
        select_element = driver.find_element_by_name(fields['wbs'])
        select_element.send_keys(exp.wbs)
        select_element.send_keys(Keys.TAB)

        #Save and Add other expense
        #logger.info('Saving expense')
        #Use TAB key to scroll down to have the Save and Add Button appear to the driver
        time.sleep(2)
        btn = driver.find_element_by_name('saveAndAddButton:container:container_body:button')
        btn.click()
        time.sleep(5)
        
        #Check if expense has been saved without error
        try:
            confirm = driver.find_element_by_css_selector('li.fbINFO')
            if 'Expense Added' in confirm.text:
                db.update_item_status(exp.uid, 'logged')
                #logger.info('Expense correctly logged: %s', exp.uid)
        except:
            db.update_item_status(exp.uid, 'error')
            #logger.error('Expense %s could not be saved', exp.uid)
            # Take a screenshot here
            #filename = 'log/screenshots/' + exp.uid + '.png'
            #driver.save_screenshot(filename)
        j += 1

    return driver

def saveExpenseReport(driver):
    """
    Saves the draft of an expense report.
    Input: driver positionned on the Add Expense form
    Output: driver closed.
    """

    #Close the Add Expense form
    #logger.info('Closing the Add Expense form')
    closeBtn = driver.find_element_by_class_name('container-close')
    closeBtn.click()

    time.sleep(2)
    #Save the draft
    #logger.info('Saving the draft of expense report')
    elts = driver.find_elements_by_class_name('actionButtonLabel')
    elts[1].click()
    time.sleep(4)

    #Logout
    #logger.info('Logging out')
    logout = driver.find_element_by_id('logoutLink')
    logout.click()

    return driver

def submitExpenseReport(driver):
    """
    Submits the expense report.
    Input: driver positionned on the Expense Report page.
    Output: driver after expense report has been submitted for approval.
    """
    #logger.info('Submitting the expense report')
    elts = driver.find_elements_by_class_name('actionButtonLabel')
    elts[0].click()
    time.sleep(2)

    #Logout
    #logger.info('Logging out')
    logout = driver.find_element_by_id('logoutLink')
    logout.click()

    return driver

def createExpensesList(activeUser):
    """
    Creates a list of Expense object for a single user.
    Input: one active user and the status ('pending')
    Output: list of Expense objects
    """

    #Getting a list of "pending expense" objects
    #------------------------------------------------------------------------------------------
    db = DBHelper()
    #logger.info('Extracting all pending expenses from expenses db')
    pending = db.extract_expenses(activeUser, 'pending')

    #Create a list of Expense objects to host the data
    #logger.info('Creating a list of expense objects')
    expObjList = [Expense() for i in range(len(pending))]

    #Transferring the data from the pending tuples to the expense objects
    i = 0
    for exp in expObjList:
        exp.amount = str(pending[i][0]).replace('.',',')        #All this jazz to convert the dot into a comma for IQ Navigator (otherwise, it logs a dot as a thousand separator).
        exp.date = pending[i][1]
        exp.reason = pending[i][2]
        exp.wbs = pending[i][3]
        exp.typex = pending[i][4]
        exp.receipt = pending[i][5]
        exp.uid = pending[i][6]
        i += 1
    
    return expObjList

def wbsCheck(activeUser, wbs):
    """
    Checks if the WBS given by the user is usable. The job creatas a $1 expense and tries to
    save it. If there is an error message, then it infers that the WBS is not valid.

    """
    userCreds = db.get_credentials(activeUser)
    
    #Initiate expense object for test
    expTest = Expense()
    expTest.amount = 1.0
    expTest.reason = 'test wbs'
    expTest.wbs = wbs
    expTest.receipt = '/var/www/expenseBot/receipts/common/fileTest.jpg'
    expTest.user = ''
    expList = [expTest]

    #logger.info('Testing the validity of the wbs')
    #Login sequence
    driver = initiateDriver()
    driver = login(driver, userCreds[0], userCreds[1])
    driver = createExpenseReport(driver)
    try:
        #logger.info('Adding the test expense to check wbs validity')
        driver = addExpense(driver, expList)
    except Exception as e:
        #logger.error('Unable to add the expense for wbs checking. %s', e)
        pass    

    #Close the Add Expense form
    closeBtn = driver.find_element_by_class_name('container-close')
    closeBtn.click()

    #Check if the expense has been saved - which proves that the WBS works
    #We get the confirmation by checking if the dataTable element displays 'No items found'

    elt = driver.find_element_by_class_name('dataTable')

    if 'No items found' not in elt.text:
        #logger.info('WBS valid')
        wbsValid = True

    elif 'No items found' in elt.text:
        #logger.info('WBS not valid')
        wbsValid = False

    #End of test
    #Try to leave gracefully
    try:
        #logger.info('Logging out, testing complete')
        logout = driver.find_element_by_id('logoutLink')
        logout.click()
    except:
        pass

    driver.quit()
    
    return wbsValid


