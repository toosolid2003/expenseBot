from datetime import date
from uuid import uuid4
import time
from currency_converter import CurrencyConverter

class Expense:
    '''The Expense object. All attributes need to be not None in order for the expense to be recorded in a database,
    or sent to an API. 
    
    It needs 5 data points as input:
    - A user name (str)
    - An amount (float)
    - A reason (str)
    - A currency (str)
    - The path to a photo or pdf file of the receipt (str).'''

    def __init__(self, user):
        self._amount = None
        self.date = date.today()
        self.uid = str(uuid4())
        self._reason = None
        self.category = 'Undetermined'
        self.ccy = None 
        self.user = user
        self._receipt = None
    
    def get_input(self, input_dict):

        
     for key, value in input_dict.items():
        if value is not None:
            print(f'{key}: {value}')
            self.__setattr__(key, value)
            


    def check_if_complete(self):
        if any(elt == None for elt in self.__dict__.values()):
            pass
        else:
            self.save_to_db()

    def save_to_db(self):
        print("expense ready to be injected")
    
    def get_user_ccy(self):
        '''Gets the default currency specified by the user. 
        Input: database where user infornation is stored
        Output: 3 character uppercase string representing the currency.'''

        return 'NZD'

    @property
    def amount(self):
        return self._amount
    
    @amount.setter
    def amount(self, val):
        
        #compare user's default ccy and input ccy. If different, perform currency conversion
        default_ccy = self.get_user_ccy()
        if default_ccy != self.ccy:
            c = CurrencyConverter()
            val = c.convert(val, self.ccy, default_ccy)
            val = round(val,2)
            self.ccy = default_ccy

        #Store amount in object
        self._amount = val
        self.check_if_complete()
    
    @property
    def reason(self):
        return self._reason

    @reason.setter
    def reason(self, r):
        self._reason = r
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
        return f'Expense data:\nAmount: {self.amount}\nUID: {self.uid}\nDate: {self.date}'