from telegram import Bot

#KEY ='/etc/letsencrypt/live/prod.expensebot.design/privkey.pem'
#CERT ='/etc/letsencrypt/live/prod.expensebot.design/fullchain.pem'


KEY = 'ssl/private.key'
CERT = 'ssl/cert.pem'
WEBHOOK = 'https://prod.expensebot.design/'

with open('bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
