from telegram import Bot

KEY ='/var/www/expenseBot/ssl/PRIVATE.key'
CERT ='/var/www/expenseBot/ssl/PUBLIC.pem'
WEBHOOK = 'https://test.expensebot.design/'

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
