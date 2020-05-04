import unittest
from botClasses.classes import Expense
from botFunctions.botLogic import *

class TestCheckCompletion(unittest.TestCase):
    def test_returnEmpty(self):
        exp = Expense()
        exp.amount, exp.reason, exp.wbs, exp.receipt, exp.user = 45, 'motel','BFG9000','/var/www/receipt/','thedropper'
        testList = checkCompletion(exp)
        self.assertEqual(len(testList), 0)

    def test_returnNotEmpty(self):
        exp = Expense()
        exp.amount, exp.reason, exp.wbs = 45, 'motel','BFG9000'
        testList = checkCompletion(exp)
        self.assertNotEqual(len(testList), 0)

class TestParsetext(unittest.TestCase):

    def testOrder1(self):
        raw = '667,Restau'
        result = parseText(raw)
        expected = {'amount':667.0,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testOrder2(self):
        raw = 'Restau,667'
        result = parseText(raw)
        expected = {'amount':667.0,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testSeparator1(self):
        raw = '667-Restau'
        result = parseText(raw)
        expected = {'amount':667.0,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testSeparator2(self):
        raw = '667;Restau'
        result = parseText(raw)
        expected = {'amount':667.0,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testSeparator3(self):
        raw = '667:Restau'
        result = parseText(raw)
        expected = {'amount':667.0,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testUniqueFloat(self):
        raw = '55'
        result = parseText(raw)
        expected = {'amount':55.0,'reason':None}
        self.assertEqual(expected, result)
    def testUniqueReason(self):
        raw = 'hotel beach'
        result = parseText(raw)
        expected = {'amount':None,'reason':'hotel beach'}
        self.assertEqual(expected, result)

    def testCents(self):
        raw = '45.76,Restau'
        result = parseText(raw)
        expected = {'amount':45.76,'reason':'Restau'}
        self.assertEqual(expected, result)

    def testExpenseFeedingAmount(self):
        raw = 'Hotel, 490'
        result = parseText(raw)
        expected = {'amount':490.0,'reason':'Hotel'}
        self.assertEqual(expected, result)

    def testExpenseFeedingReason(self):
        raw = 'Hotel, 490'
        result = parseText(raw)
        expected = {'amount':490.0,'reason':'Hotel'}
        self.assertEqual(expected, result)

    def testCurrencyConvert(self):
        raw = '45 eur, train'
        expected = {'amount': 47.7,'reason':'train'}
        result = parseText(raw)
        self.assertEqual(result, expected)

    def testCurrencyConvertUnique(self):
        raw = '45 eur'
        expected = {'amount':47.7,'reason':None}
        result = parseText(raw)
        self.assertEqual(expected, result)

class testDeductType(unittest.TestCase):

    def testAccomodationApartment(self):
        exp = Expense()
        exp.reason = 'Airbnb'
        exp = deductType(exp)
        self.assertEqual(exp.type, '17819672005')

    def testAccomodationHotel(self):
        exp = Expense()
        exp.reason = 'Hotel Accapulco'
        exp = deductType(exp)
        self.assertEqual(exp.type, '17819670115')

    def testAirfare(self):
        exp = Expense()
        exp.reason = 'Flight Zurich'
        exp = deductType(exp)
        self.assertEqual(exp.type, '17819684336')

    def testPerdiemsDomestic(self):
        exp = Expense()
        exp.reason = 'per diem welly'
        exp = deductType(exp)
        self.assertEqual(exp.type,'17819687871')


 
#class TestEmailParser(unittest.TestCase):
#    def testEasyjetParseAmount(self):
#        filePath = 'easyjet-2020-04-10.json'
#        result = parseFlightEmail(filePath)
#        expected = Expense()
#        expected.amount = '69.00'
#        self.assertEqual(result.amount, expected.amount)
#
#    def testEasyjetParseReason(self):
#        filePath = 'easyjet-2020-04-10.json'
#        result = parseFlightEmail(filePath)
#        expected = Expense()
#        expected.reason = 'flight Amsterdam to Basel-Mulhouse-Freiburg'
#        self.assertEqual(result.reason, expected.reason)
#
#
if __name__ == '__main__':
    unittest.main()
