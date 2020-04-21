#coding: utf-8
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


def addExpense(driver, exp):
    """
    Records a new expense in the Add Expense form.
    Input: browser (driver) with Add Expense form open, expense objet
    Output: browser (driver) after all expenses are recorded.

    """

def saveExpenseReport(driver):
    """
    Saves the draft of an expense report.
    Input: driver positionned on the Expense Report page.
    Output: driver after expense report is saved
    """

def submitExpenseReport(driver):
    """
    Submits the expense report.
    Input: driver positionned on the Expense Report page.
    Output: driver after expense report has been submitted for approval.
    """

