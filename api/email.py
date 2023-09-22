from api.connector import Connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from threading import Thread

class Email:
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender = 'mestount@gmail.com'
    password = 'iquduhyskpuadboe'
    server = SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
        
    @Connector.sync_catch_error
    def send_mail(to, message):
        pass
    
    @Connector.sync_catch_error
    def message(to, subject, body):
        message = MIMEMultipart()
        message['From'] = Email.sender
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
        
        if not Email.server:
            print('loading server')
            if isinstance(Email.load_server(), dict):
                raise Exception('Erro de conexão')
            
        Email.server.sendmail(
            Email.sender,
            to,
            message.as_string()
        )
        
