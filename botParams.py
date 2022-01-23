KEY ='/var/www/expenseBot/ssl/PRODPRIVATE.key'
CERT ='/var/www/expenseBot/ssl/PRODPUBLIC.pem'
WEBHOOK = 'https://prod.expensebot.design/'

<<<<<<< HEAD
=======
KEY ='/var/www/expenseBot/ssl/PRIVATE.key'
CERT ='/var/www/expenseBot/ssl/PUBLIC.pem'
WEBHOOK ='https://test.expensebot.design/'

with open('/var/www/expenseBot/bot.token','r') as fichier:
    token = fichier.read()
    TOKEN = token.replace('\n','')

bot = Bot(TOKEN)
>>>>>>> 2162bd0107abb8c36182f00f6ac711e1fcb6d3ac
