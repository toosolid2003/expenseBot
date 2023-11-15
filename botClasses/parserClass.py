import os
import re

#Constants
MANAGEDCCY = ['usd','chf','aud','nzd','rub','eur','cad','rub','uah']

class Parser():

    def __init__(self):
        self.raw = None
        self.resultList = None 
        self.result = {
            'ccy': None,
            'reason': None,
            'receipt': None,
            'category': None, 
            'amount': None,
        }
    def parse_text(self, raw):
        '''Parse text sent by the user. Feeds the results dictionnary'''
        self.raw = raw
        self.resultList = self.split_text()
        self.result = {
           'ccy': self.get_ccy(MANAGEDCCY),
           'reason': self.get_reason(),
           'receipt': None,
           'category': self.get_category(),
           'amount': self.get_amount(),
        }
    
    def parse_picture(self, f, telegram_username, bot):
         
        '''Saves a document on the local disk and returns a filepath to be stored in the database.
        Input: Telegram file_id, telegram_username and Telegram bot instance
        Output: absolute_path_to_file'''

        #Change the current directory to one which www-data has access to
        #cwd = os.getcwd()
        os.chdir('receipts/' + telegram_username)

        #Download the file
        try:
            filename = bot.get_file(file_id=f).download()
        except Exception as e:
            print(f"Could not save file: {e}")

        path = os.getcwd() + '/' + filename
        print(f'Document is saved as {path}')

        #Going back to the main directory
        os.chdir('../..')

        self.result['receipt'] = path


    def split_text(self):
        '''Split the input string with a series of delimiters. 
        Returns a list of splitted words'''

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
        
        splitted_input = re.split(r"[,;:]{1}", self.raw)
        return splitted_input[1].strip()

    def get_category(self):
        '''Bug for the per diem: since the mechanism only searches for one word at a tinme, 2 words expressions like "per diem"
        get through unnoticed.'''

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

 
if __name__ == "__main__":
    p = Parser()
    p.parse_text('45 eur, restaurant')
    print(p.__dict__)