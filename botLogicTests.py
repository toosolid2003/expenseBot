import unittest
from botClasses.classes import Expense, DBHelper
from botFunctions.botLogic import *

class TestCheckCompletion(unittest.TestCase):
    def test_returnEmpty(self):
        dic = {'amount':45.0, 'reason':'motel','wbs':'BFG9000','receipt':'/var/www/receipt/','user':'thedropper','typex':'17819670115'}
        testBool = checkCompletion(dic)
        self.assertTrue(testBool)

    def test_returnNotEmpty(self):
        dic = {'reason':'motel','wbs':'BFG9000','receipt':'/var/www/receipt/','user':'thedropper','typex':'17819670115'}
        testBool = checkCompletion(dic)
        self.assertFalse(testBool)

class TestParsetext(unittest.TestCase):

    def testOrder1(self):
        raw = '667,Restau'
        result = parseText(raw,'thedropper')
        expected = {'amount':667.0,'reason':'Restau', 'typex':'food & beverage'}
        self.assertEqual(expected, result)

    def testOrder2(self):
        raw = 'Restau,667'
        result = parseText(raw,'thedropper')
        expected = {'amount':667.0,'reason':'Restau', 'typex':'food & beverage'}
        self.assertEqual(expected, result)

    def testSeparator2(self):
        raw = '667;Restau'
        result = parseText(raw,'thedropper')
        expected = {'amount':667.0,'reason':'Restau', 'typex':'food & beverage'}
        self.assertEqual(expected, result)

    def testSeparator3(self):
        raw = '667:Restau'
        result = parseText(raw,'thedropper')
        expected = {'amount':667.0,'reason':'Restau', 'typex':'food & beverage'}
        self.assertEqual(expected, result)

    def testUniqueFloat(self):
        raw = '55'
        result = parseText(raw,'thedropper')
        expected = {'amount':55.0,'reason':None, 'typex': None}
        self.assertEqual(expected, result)

    def testUniqueReason(self):
        raw = 'hotel beach'
        result = parseText(raw,'thedropper')
        expected = {'amount':None,'reason':'hotel beach', 'typex':'accomodation'}
        self.assertEqual(expected, result)

    def testCents(self):
        raw = '45.76,Restau'
        result = parseText(raw,'thedropper')
        expected = {'amount':45.76,'reason':'Restau', 'typex':'food & beverage' }
        self.assertEqual(expected, result)

    def testExpenseFeedingAmount(self):
        raw = 'Hotel, 490'
        result = parseText(raw,'thedropper')
        expected = {'amount':490.0,'reason':'Hotel', 'typex':'accomodation'}
        self.assertEqual(expected, result)

    def testExpenseFeedingReason(self):
        raw = 'Hotel, 490'
        result = parseText(raw,'thedropper')
        expected = {'amount':490.0,'reason':'Hotel', 'typex':'accomodation'}
        self.assertEqual(expected, result)

    def testCurrencyConvert(self):
        raw = '45 eur, train'
        expected = {'amount': 47.7,'reason':'train', 'typex': 'transportation'}
        result = parseText(raw,'thedropper')
        self.assertEqual(result, expected)

    def testCurrencyConvertUnique(self):
        raw = '45 eur'
        expected = {'amount':47.7,'reason':None, 'typex': None}
        result = parseText(raw,'thedropper')
        self.assertEqual(expected, result)

class testDeductType(unittest.TestCase):
    
    def testAccomodationApartment(self):
        reason = 'Airbnb'
        expectedType = getType(reason)
        self.assertEqual(expectedType, 'accomodation')

    def testAccomodationHotel(self):
        reason = 'Hotel Accapulco'
        expectedType = getType(reason)
        self.assertEqual(expectedType, 'accomodation')

    def testAirfare(self):
        reason = 'Flight Zurich'
        expectedType = getType(reason)
        self.assertEqual(expectedType, 'flight')

    def testPerdiemsDomestic(self):
        reason = 'per diem welly'
        expectedType = getType(reason)
        self.assertEqual(expectedType,'per diem')


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
