# coding: utf-8
from botFunctions.iqnCommands import *
driver = login('tsegura2','Brutasse1-')
driver = createExpenseReport(driver)
pd = createExpensesList('thedropper')
driver = addExpense(driver, pd)
driver = saveExpenseReport(driver)
