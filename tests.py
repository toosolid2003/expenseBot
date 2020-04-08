import unittest
from classes import Expense
from functions import checkCompletion, parseText

class TestCheckCompletion(unittest.TestCase):
    def test_returnEmpty(self):
        exp = Expense()
        exp.amount, exp.reason, exp.wbs, exp.receipt = 45, 'motel','BFG9000',b'testave'
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
        expected = (667.0,'Restau')
        self.assertEqual(expected, result)

    def testOrder2(self):
        raw = 'Restau,667'
        result = parseText(raw)
        expected = (667.0,'Restau')
        self.assertEqual(expected, result)

    def testSeparator1(self):
        raw = '667-Restau'
        result = parseText(raw)
        expected = (667.0,'Restau')
        self.assertEqual(expected, result)

    def testSeparator2(self):
        raw = '667;Restau'
        result = parseText(raw)
        expected = (667.0,'Restau')
        self.assertEqual(expected, result)

    def testSeparator3(self):
        raw = '667:Restau'
        result = parseText(raw)
        expected = (667.0,'Restau')
        self.assertEqual(expected, result)
    def testCents(self):
        raw = '45.76,Restau'
        result = parseText(raw)
        expected = (45.76,'Restau')
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
