from datetime import datetime
import openpyxl
from os import path
import zipfile
import time

class ExpenseReport:
    
    def __init__(self, user):
        self.date = datetime.today()
        self.timestamp = int(time.time())
        self.format = '.xlsx'
        self.template = '/var/www/expenseBot/exports/exportTemplate.xlsx'
        self.total = None
        self.user = user
        self.receiptsPath = None
        self.reportPath = None

    def generate(self, expenseList):
        
        """Generates an expense report. 

        Input: list of expenses
        Output: absolute path to the expense report"""

        #Loading the excel template
        wb = openpyxl.load_workbook(filename=self.template)
        ws = wb.active
        row = 19
        col = 2

        #Converting the result into a list of lists to allow reformatting later on
        exp = []
        for elt in expenseList:
            exp.append(list(elt))

        #Reformating the 'receipts' string to remove the abosulte path
        for elt in exp:
            elt[5] = path.basename(elt[5])


        #Format the receipt column to remove the whole path
        for reason, amount, currency, date, typex, receipt in exp:
            ws.cell(row, col).value = reason
            ws.cell(row, col + 1).value = amount
            ws.cell(row, col + 2).value = currency
            ws.cell(row, col + 3).value = date
            ws.cell(row, col + 4).value = typex
            ws.cell(row, col + 5).value = receipt
            row += 1

        #Saving the file
        self.reportPath = '/var/www/expenseBot/exports/' + self.user + '/' + 'expenseReport_' + str(self.timestamp) + self.format
        wb.save(self.reportPath)

        return self.reportPath
    
    def receiptZip(self, expenseList):
        '''Gets the receipts for the expense report of the object.'''

        #Flename creation
        self.receiptsPath = '/var/www/expenseBot/exports/' + self.user + '/' + 'receiptsExports_' + str(self.timestamp) + '.zip'

        #Creating the zipfile
        with zipfile.ZipFile(self.receiptsPath,'x') as myzip:
            for expense in expenseList:
                myzip.write(expense[5], path.basename(expense[5]))   #The path of the receipt is in 5th position in the expense list
    
        #Return the file path
        return self.receiptsPath
 
    
    def send(self, email, expenseReport, receipts):
        '''Sends the expense report with corresponding receipts using the SendGrid platform
        
        Input: destination email, path pf the expense report, path of the archive containing the receipts
        Output: feedback code sent by SendGrid'''