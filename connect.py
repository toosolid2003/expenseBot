# coding: utf-8
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time

#Login sequence
'''Enters expenses on IQ Navigator. Needs a collection of expenses as input.'''

driver = Chrome()
driver.get('https://augustus.iqnavigator.com/wicket/wicket/page?x=s89lP8StUfw')
element = driver.find_element_by_id('username')
element.send_keys('tsegura2')
elemental = driver.find_element_by_id('password')
elemental.send_keys('Brutasse1-')
elemental.send_keys(Keys.RETURN)


#Home page
time.sleep(10)

# Click on 'Create Expense Report' from Home page
lb = driver.find_elements_by_class_name('launchButton')
lb[1].click()

# Click on Create expense report from Assignment page
bt = driver.find_elements_by_class_name('actionButtonLabel')
bt[0].click()

#Add expense button
bt = driver.find_elements_by_class_name('actionButtonLabel')
bt[2].click()
time.sleep(5)
# ------------------------------------------------------------
# Add Expense form
## Enter date

label = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:1:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textBox')
label.send_keys('21-3-2020')
time.sleep(2)

#Enter Amount
label = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:3:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField')
label.send_keys('150')
time.sleep(2)

#Enter reason
label = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:4:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField')
label.send_keys('Hotel Zurich')
time.sleep(2)

#Upload receipt
btn = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileInput')
btn.send_keys('/Users/t.segura/Documents/Code/expenseBot/expense_2020_03_23.jpg')
time.sleep(10)  #Wait for receipt to load
#Click on 'Attach' button
buttn = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:5:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:container:attachmentPanel:feedback:border:feedback_body:fileSubmit:container:container_body:button')
buttn.click()

#Enter WBS
time.sleep(2)
select_element = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:7:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:sizingWrapper:textField:autocompleteField')
select_element.send_keys('BLPBX001')
time.sleep(2)

#Enter type (html select)
select_element = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:2:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:select')
select_object = Select(select_element)
select_object.select_by_visible_text('Airfare')
time.sleep(2)


#Click on Save and create new expense
#btn = driver.find_element_by_id('idd6')
#btn.click()


#Save and Close
#btn = driver.find_element_by_id('idd8')
#btn.click()
##Logout
#logout = driver.find_element_by_id('logoutLink')
#logout.click()
saveNclose = driver.find_element_by_name('saveAndCloseButton:container:container_body:button')
saveNclose.click()
