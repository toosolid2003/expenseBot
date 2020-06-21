import logging

logger = logging.getLogger('expenseBotLogger')
logger.setLevel(logging.DEBUG)

#Define format of loggers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')



#Create a log file that captures all events of DEBUG importance and above
#This is the most detailed log

debugLog = logging.FileHandler('/var/www/expenseBot/log/detailedInfo.log')
debugLog.setLevel(logging.DEBUG)
debugLog.setFormatter(formatter)


#Add these handler to logger object
logger.addHandler(debugLog)
