from telegram import Bot

KEY ='/var/www/expenseBot/ssl/PRODPRIVATE.key'
CERT ='/var/www/expenseBot/ssl/PRODPUBLIC.pem'
WEBHOOK = 'https://prod.expensebot.design/'

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
