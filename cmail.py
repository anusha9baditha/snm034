import smtplib
from email.message import EmailMessage
def send_mail(to,subject,body):
    try:
        server=smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.login('anusha@codegnan.com','ghfc ectt mlqa ucwl')
        msg=EmailMessage()
        msg['FROM']='anusha@codegnan.com'
        msg['SUBJECT']=subject
        msg['TO']=to
        msg.set_content(body)
        server.send_message(msg)
        print('mail sent')
        server.close()
    except Exception as e:
        print('Mail Error',e)
