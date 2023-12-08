from datetime import date
from uuid import uuid4
import time
from currency_converter import CurrencyConverter, ECB_URL
import urllib.request
from logger.logger import logger

class Expense:
    '''The Expense object. All attributes need to be not None in order for the expense to be recorded in a database,
    or sent to an API. 
    
    It needs 5 data points as input:
    - A user name (str)
    - An amount (float)
    - A description (str)
    - A currency (str)
    - The path to a photo or pdf file of the receipt (str).'''

    def __init__(self, user):
        self._amount = None
        self.date = date.today()
        self.uid = str(uuid4())
        self._description = None
        self.category = 'Undetermined'
        self.ccy = self.get_user_ccy() 
        self.user = user
        self._receipt = None
        self.complete = False
    
    def get_input(self, input_dict):

        
     for key, value in input_dict.items():
        if value is not None:
            self.__setattr__(key, value)
            


    def check_if_complete(self):
        if any(elt == None for elt in self.__dict__.values()):
            logger.debug(f"Missing an attribute")
        else:
            self.complete = True
            self.save_to_db()

    def save_to_db(self):
        print("expense ready to be injected")
    

    
    def get_user_ccy(self):
        '''Gets the default currency specified by the user. 
        Input: database where user infornation is stored
        Output: 3 character uppercase string representing the currency.'''

        return 'USD'
    
    def pull_latest_rates(self):
        '''Get the latest currency conversion rates from the ECB. 
        Returns a CurrencyConverter object.'''

        filename = f"ecb_{date.today():%Y%m%d}.zip"
        urllib.request.urlretrieve(ECB_URL, filename)
        c = CurrencyConverter(filename)
        return c
    

    @property
    def amount(self):
        return self._amount
    
    @amount.setter
    def amount(self, val):
        
        #compare user's default ccy and input ccy. If different, perform currency conversion
        # default_ccy = self.get_user_ccy()
        # if default_ccy != self.ccy:
        #     c = CurrencyConverter()
        #     val = c.convert(val, self.ccy, default_ccy)
        #     val = round(val,2)
        #     self.ccy = default_ccy

        #Store amount in object
        self._amount = val
        self.check_if_complete()
    
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, r):
        self._description = r
        self.check_if_complete()
    
    @property
    def receipt(self):
        return self._receipt

    @receipt.setter
    def receipt(self, r):
        self._receipt = r 
        self.check_if_complete()
    

    #this method just for fun
    def __repr__(self):
        return f'Expense data:\nAmount: {self.amount}\nUID: {self.uid}\nDate: {self.date}\nReceipt: {self.receipt}\nCcy: {self.ccy}\nCategory: {self.category}\ndescription: {self.description}\nComplete: {self.complete}'