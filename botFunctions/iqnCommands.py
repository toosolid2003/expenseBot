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
import logging
from botClasses.classes import *

def login(username, password):

    print('Initialising Chrome driver')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--window-size=1920,1080");
    chrome_options.add_argument("--start-maximized");
    driver = Chrome(options=chrome_options)
    print('Logging expenses for {}'.format('Thibaut'))
    
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
   
    return driver

def createExpenseReport(driver):
    """
    Create a new expense report in IQ Navigator.

    Input: browser (driver) positionned on IQN Home Page
    Output: browser (driver) with Add Expense form open

    """

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

    # Add Expense form - start of the loop
    j = 0
    ## Enter date
    for exp in expObjList:

        print('Adding expense {}'.format(j))

        #Enter type (html select)
        print('Adding type: {}'.format(exp.type))
        select_element = driver.find_element_by_name(fields['type'])
        select_object = Select(select_element)
#        select_object.select_by_visible_text(exp.type)
        select_object.select_by_value(exp.type)
        time.sleep(2)

        #Enter date of expense
        print('Adding date: {}'.format(exp.date))
        label = driver.find_element_by_name(fields['date'])
        label.send_keys(exp.date)
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Enter Amount
        print('Adding amount: {}'.format(exp.amount))
        label = driver.find_element_by_name(fields['amount'])
        label.send_keys(str(exp.amount))
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Enter reason
        print('Adding reason: {}'.format(exp.reason))
        label = driver.find_element_by_name(fields['reason'])
        label.send_keys(exp.reason)
        #label.send_keys(Keys.TAB)
        #time.sleep(2)

        #Upload receipt
        print('Uploading receipt: {}'.format(exp.receipt))
        btn = driver.find_element_by_name(fields['receipt'])
        btn.send_keys(exp.receipt)
        time.sleep(2)

        #Click on 'Attach' button
        buttn = driver.find_element_by_name(fields['attachBtn'])
        buttn.click()
        time.sleep(4)  #Wait for receipt to load

        #Enter WBS
        print('Adding WBS: {}'.format(exp.wbs))
        select_element = driver.find_element_by_name(fields['wbs'])
        select_element.send_keys(exp.wbs)
        select_element.send_keys(Keys.TAB)

        #Save and Add other expense
        print('Saving expense')
        #Use TAB key to scroll down to have the Save and Add Button appear to the driver
        time.sleep(2)
        btn = driver.find_element_by_name('saveAndAddButton:container:container_body:button')
        btn.click()
        time.sleep(5)
#        #Take a screenshot here
#        driver.save_screenshot('diagnostic.png')
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

    return driver

def saveExpenseReport(driver):
    """
    Saves the draft of an expense report.
    Input: driver positionned on the Add Expense form
    Output: driver closed.
    """

    #Close the Add Expense form
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

    return driver

def submitExpenseReport(driver):
    """
    Submits the expense report.
    Input: driver positionned on the Expense Report page.
    Output: driver after expense report has been submitted for approval.
    """
    return driver

def createExpensesList(activeUser):
    """
    Creates a list of Expense object for a single user.
    Input: one active user
    Output: list of Expense objects
    """

    #Getting a list of "pending expense" objects
    #------------------------------------------------------------------------------------------
    db = DBHelper()
    pending = db.extract_pending(activeUser)

    #Create a list of Expense objects to host the data
    expObjList = [Expense() for i in range(len(pending))]

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
    
    return expObjList
