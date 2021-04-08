# coding: utf-8
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId)
import base64

#variables: 
# - filepath
# - email of sender
# - email of recipient

def sendExport(emailSender, emailRecipient, filepath=None):
    """
    Send an email with attatchment to specified recipient with sendGrid.
    Input: email of sender, email of recipient, optional:filepath of attachment
    Output: reponse code

    Make sure that the email of sender has been verified on sendGrid.
    """
    #Initiate constants and objects

    API = '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'
    sg = SendGridAPIClient(api_key=API)

    #Creating Mail object
    message = Mail(
        from_email = emailSender,
        to_emails= emailRecipient,
        subject = 'Your csv export',
        html_content = '<strong>Here is your csv export from expenseBot.net</strong>'
        )

    #Creating attachment
    if filepath != None:
        with open(filepath, 'rb') as f:
            data = f.read()
            f.close()

        encoded_file = base64.b64encode(data).decode()

        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName('yourExport.csv'),
            FileType('text/csv'),
            Disposition('attachment')
            )

        message.add_attachment(attachedFile)

    #Sending the email

    response = sg.send(message)

    return response