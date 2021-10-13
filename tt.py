# coding: utf-8
from botFunctions.export_mail import *
import datetime
db = DBHelper()
d = datetime.date(2021,5,6)
data = db.extract_exp_date('thedropper',d)
l = []
for elt in data:
    l.append(list(elt))
    
formatExport(l)
