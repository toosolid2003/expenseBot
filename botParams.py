from telegram import Bot


KEY = 'ssl/private.key'
CERT = 'ssl/cert.pem'
WEBHOOK = 'https://prod.expensebot.design/'

with open('bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
