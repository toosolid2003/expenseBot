# coding: utf-8
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time

#Login sequence
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

label = driver.find_element_by_id('idcd')
label.send_keys('21-3-2020')

#Enter Amount
label = driver.find_element_by_id('idd0')
label.send_keys('150')

#Enter reason
label = driver.find_element_by_name('entryFieldsContainer:fieldGroup:fields:4:feedbackReportingBorder:border:feedbackReportingBorder_body:fieldWrapper:field:textField')
label.send_keys('Hotel Zurich')

#Upload receipt

#Enter WBS
time.sleep(2)
select_element = driver.find_element_by_id('idcc')
select_element.send_keys('BJNBG001')

#Enter type (html select)
select_element = driver.find_element_by_id('idce')
select_object = Select(select_element)
select_object.select_by_visible_text('Airfare')


#Click on Save and create new expense
btn = driver.find_element_by_id('idd6')
#btn.click()


#Save and Close
#btn = driver.find_element_by_id('idd8')
#btn.click()
##Logout
#logout = driver.find_element_by_id('logoutLink')
#logout.click()
