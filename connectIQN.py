# coding: utf-8
import selenium
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
import logging
from classes import *
from functions import *

#Set up logging module
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


#Creating a dictionnary to host the names of the fields on the Add Expense form
fields = {'date':'entryFieldsContainer:fieldGroup:fields:1:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textBox',
        'amount':'entryFieldsContainer:fieldGroup:fields:3:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField',
        'reason':'entryFieldsContainer:fieldGroup:fields:4:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField',
        'receipt':'entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileInput',
        'attachBtn':'entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileSubmit:container:container_body:button',
        'wbs':'entryFieldsContainer:fieldGroup:fields:7:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:sizingWrapper:textField:autocompleteField',
        'type':'entryFieldsContainer:fieldGroup:fields:2:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:select'}

#------------------------------------------------------------------------------------------

#Getting a list of active users
#------------------------------------------------------------------------------------------


userdb = userDB()
activeUsers = userdb.get_users_by_status('active')

#------------------------------------------------------------------------------------------

#Inject expenses for each active user:

userCount = 0
db = DBHelper()

for user in activeUsers:
    #Getting a list of "pending expense" objects
    #------------------------------------------------------------------------------------------

    activeUserTelegram = activeUsers[userCount][0]
    pending = db.extract_pending(activeUserTelegram)

    #Create a list of Expense objects to host the data
    expObjList = [Expense() for i in range(len(pending))]

    nbExpensesDB = len(pending)
    #Transferring the data from the pending tuples to the expense objects
    i = 0
    for exp in expObjList:
        exp.amount = str(pending[i][0]).replace('.',',')        #All this jazz to convert the dot into a comma for IQ Navigator (otherwise, it logs a dot as a thousand separator).
        exp.date = pending[i][1]
        exp.reason = pending[i][2]
        exp.wbs = pending[i][3]
        exp.type = pending[i][4]
        exp.receipt = pending[i][5]
        i += 1

    #Assign variables
    username = activeUsers[userCount][1]
    password = activeUsers[userCount][2]
    
    #Initiating the Chrome driver
    print('Initialising Chrome driver')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--window-size=1920,1080");
    chrome_options.add_argument("--start-maximized");
    driver = Chrome(options=chrome_options)
    print('Logging expenses for {}'.format(activeUserTelegram))

    #Login sequence
    print('Opening the login page')
    driver.get('https://augustus.iqnavigator.com/wicket/wicket/page?x=s89lP8StUfw')
    element = driver.find_element_by_id('username')
    element.send_keys(username)
    elemental = driver.find_element_by_id('password')
    elemental.send_keys(password)
    elemental.send_keys(Keys.RETURN)
    print('Logging in...')

    #Home page - wait for the logout element to load before doing anything
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'logoutLink')))
    print('Logged in. On Home Page')
    # Click on 'Create Expense Report' from Home page
    bt = driver.find_element_by_link_text('Create Expense Report')
    bt.click()

    # Click on Create expense report from Assignment page
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'actionButtonLabel')))
    bt = driver.find_elements_by_class_name('actionButtonLabel')
    bt[0].click()
    time.sleep(3)

    #Enter a title for the Expense Report
    print('Creating a new expense report')
    expReportTile = driver.find_element_by_name('expenseReportEditPanel:border:border:content:border_body:fieldGroup:repeater:1:fieldWLOT:textField')
    expReportTile.send_keys('Expenses for this week')

    #Add expense button
    bt = driver.find_elements_by_class_name('actionButtonLabel')
    bt[2].click()
    time.sleep(5)
    print('Adding Expenses...')

    # ------------------------------------------------------------


    # Add Expense form - start of the loop
    j = 0
    ## Enter date
    for exp in expObjList:

        print('Adding expense {}'.format(j))
        print('Adding date: {}'.format(exp.date))
        label = driver.find_element_by_name(fields['date'])
        label.send_keys(exp.date)
        time.sleep(2)

        #Enter Amount
        print('Adding amount: {}'.format(exp.amount))
        label = driver.find_element_by_name(fields['amount'])
        label.send_keys(str(exp.amount))
        time.sleep(2)

        #Enter reason
        print('Adding reason: {}'.format(exp.reason))
        label = driver.find_element_by_name(fields['reason'])
        label.send_keys(exp.reason)
        time.sleep(2)

        #Upload receipt
        print('Uploading receipt: {}'.format(exp.receipt))
        btn = driver.find_element_by_name(fields['receipt'])
        btn.send_keys(exp.receipt)
        time.sleep(2)

        #Click on 'Attach' button
        buttn = driver.find_element_by_name(fields['attachBtn'])
        buttn.click()
        time.sleep(5)  #Wait for receipt to load

        #Enter type (html select)
        print('Adding type: {}'.format(exp.type))
        select_element = driver.find_element_by_name(fields['type'])
        select_object = Select(select_element)
        select_object.select_by_visible_text(exp.type)
        time.sleep(2)


        #Enter WBS
        print('Adding WBS: {}'.format(exp.wbs))
        select_element = driver.find_element_by_name(fields['wbs'])
        select_element.send_keys(exp.wbs)
        #Truc sioux pour activer le js dans le champ WBS
        #label = driver.find_element_by_name(fields['reason'])
        #time.sleep(5)

        #Save and Add other expense
        print('Saving expense')
        #Use TAB key to scroll down to have the Save and Add Button appear to the driver
        select_element.send_keys(Keys.TAB)
        time.sleep(2)
        btn = driver.find_element_by_name('saveAndAddButton:container:container_body:button')
        btn.click()
        time.sleep(5)
#        #Take a screenshot here
        driver.save_screenshot('diagnostic.png')
#        try:
#            feedback = driver.find_element_by_class_name('fbERROR')
#            print('Error on the form')
#        except NoSuchElementException:
#            feedback = driver.find_element_by_class_name('fbINFO')
#            print('Expense recorded, off to the next')
        #Save and Close
        #saveNclose = driver.find_element_by_name('saveAndCloseButton:container:container_body:button')
        #saveNclose.click()
        time.sleep(2)
        j += 1

    #Close the Add Expense modal
    closeBtn = driver.find_element_by_class_name('container-close')
    closeBtn.click()

    time.sleep(2)
    #Save the draft
    print('Saving the draft of expense report')
    elts = driver.find_elements_by_class_name('actionButtonLabel')
    elts[1].click()
    time.sleep(4)

    #Logout
    print('Logging out')
    logout = driver.find_element_by_id('logoutLink')
    logout.click()

    #Close Chrome
    driver.close()

    #Update the database: change the status of logged expenses
    print('Updating the database')
    upDb = DBHelper()
    upDb.updateStatus("pending","logged",activeUserTelegram)

    userCount += 1
#Printint number of logged expenses
print("Number of expensed logged into IQN: {}/{}".format(j, nbExpensesDB))
