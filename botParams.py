from telegram import Bot

#KEY ='/etc/letsencrypt/live/prod.expensebot.design/privkey.pem'
#CERT ='/etc/letsencrypt/live/prod.expensebot.design/fullchain.pem'


KEY = '/var/www/expenseBot/ssl/private.key'
CERT = '/var/www/expenseBot/ssl/cert.pem'
WEBHOOK = 'https://prod.expensebot.design/'

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
