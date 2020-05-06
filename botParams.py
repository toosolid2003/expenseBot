from telegram import Bot

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    token = token.replace('\n','')

bot = Bot(token)
