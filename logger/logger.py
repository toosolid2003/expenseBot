import logging

logger = logging.getLogger('expenseBotLogger')
logger.setLevel(logging.DEBUG)

#Define format of loggers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')



#Create a log file that captures all events of INFO importance and above
#This is the most detailed log

infoLog = logging.FileHandler('/var/www/expenseBot/log/detailedInfo.log')
infoLog.setLevel(logging.INFO)
infoLog.setFormatter(formatter)



#Create a log file to only capture ERROR messages

errorLog = logging.FileHandler('/var/www/expenseBot/log/errorLog.log')
errorLog.setLevel(logging.ERROR)
errorLog.setFormatter(formatter)


#Add these handler to logger object
logger.addHandler(infoLog)
logger.addHandler(errorLog)
