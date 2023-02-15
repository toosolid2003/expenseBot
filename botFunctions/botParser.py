from botFunctions.botData.parserData import *

class Parser:

    def __init__(self, textInput):
        self.input = None
        self.split = textInput.split()
        self.ccy = None
        self.typex = None
        self.amount = None
    
    def getCcy(self):
        self.ccy = set(self.split) & set(managedCcy)
    
    def getType(self):
        for elt in types.values():
            res = set(elt) & set(self.split)
            if len(res) > 0:
               return res 
    
    def getAmount(self):
        for elt in self.split:
            try:
                self.amount = float(elt)
            except:
                pass
    