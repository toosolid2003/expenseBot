import os
import re
from logger.logger import logger

#Constants
MANAGEDCCY = ['usd','chf','aud','nzd','rub','eur','cad','rub','uah']

class Parser():

    def __init__(self, raw):
        self.raw = raw
        self.resultList = self.split_text() 
        self.result = {
            'ccy': self.get_ccy(MANAGEDCCY),
            'reason': self.get_reason(),
            'receipt': None,
            'category': self.get_category(),
            'amount': self.get_amount(),
        }

    def split_text(self):
        
        return re.split(r'[:,;\s]\s*', self.raw)

    def get_amount(self):
        for elt in self.resultList:
            try:
                # self.result["amount"] = round(float(elt),2)
                return round(float(elt),2)
            except:
                pass
    
    def get_ccy(self, managedCcy):

        for elt in self.resultList:
            if elt in managedCcy:
                return elt.upper()

    def get_reason(self):
        splitted_input = re.split(r"[,.;:]{1}", self.raw)
        return splitted_input[1].strip()

    def get_category(self):
        types = {'accomodation' :['airbnb','apartment','hotel','pension','hostel'],
           'transportation':['taxi','uber','lyft','train','bus','ferry','sbb','eurostar','sncf','thalys'],
   'flight':['plane','flight','easyjet','klm','airfrance','flights','ryanair','lufthansa'],
   'car rental':['avis','entreprise','rental car','alamo', 'car rental','car'],
   'food & beverage':['drinks','bar','restaurant','restau','sandwich','sandwiches','meal','dinner','lunch','breakfast'],
   'car expenses':['toll','parking','fuel','highway','public','gas','petrol'],
   'per diem':['perdiem', 'per diem','per diems','perdiems']
   }

        expenseType = 'various'
        for title, typeList in types.items(): 
            for elt in self.resultList: 
                if elt in typeList: 
                    expenseType = title
        return expenseType

    def parse_with_ai(self):
        pass

    def get_receipt(self, fileId, telegram_username, bot):
        '''Saves a document on the local disk and returns a filepath to be stored in the database.
        Input: Telegram file_id, telegram_username and Telegram bot instance
        Output: absolute_path_to_file'''

        #Change the current directory to one which www-data has access to
        # cwd = os.getcwd()
        os.chdir('receipts/' + telegram_username)
        print(os.getcwd())

        #Download the file
        try:
            filename = bot.get_file(fileId).download()
        except Exception as e:
            logger.error('Could not download file %s. Error: %s', fileId, e)

        filename = os.getcwd() + '/' + filename
        logger.debug(f'Document is saved as {filename}')

        #Going back to the main directory
        os.chdir('../..')
        
        self.result['receipt'] = filename

if __name__ == "__main__":
    p = Parser('15 usd, restaurant with Johnny')
    print(p.__dict__)