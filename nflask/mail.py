from flask_mail import Mail, Message

mail = Mail()
    
def send_mail(title,recipents,body):
    msg = mail.send_message(
        subject=title,
        recipients=recipents,
        body=body
    )
    return 'Mail sent'
