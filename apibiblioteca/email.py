"""
# apibiblioteca.email

This module contains the Email class, that have a function to send emails asynchronously.
"""

from asyncio import to_thread
from .utils import EMAIL_PASSWORD, EMAIL_SENDER
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

class Email:
    """
    # apibiblioteca.email.Email
    
    This class contains constants associated to the method used for sendind
    """
    
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER = EMAIL_SENDER
    PASSWORD = EMAIL_PASSWORD
    SERVER = SMTP(SMTP_SERVER, SMTP_PORT)
    SERVER.starttls()
    SERVER.login(SENDER, PASSWORD)
    
    def load_server(func):
        async def wrapper(*args, **kwargs):
            while Email.SERVER == None:
                print('[CONNECTING TO SMTP SERVER]')
                try:
                    Email.SERVER = SMTP(Email.SMTP_SERVER, Email.SMTP_PORT)
                    Email.SERVER.starttls()
                    Email.SERVER.login(Email.SENDER, Email.PASSWORD)
                    print('[CONNECTED TO SMTP SERVER]')
                    break
                except Exception as e:
                    print('[AN ERROR OCURRED]\n', e, '\n[TRYING AGAIN]')
            return await func(*args, **kwargs)
        return wrapper
    
    @load_server
    async def message(to: str, body: str, subject: str="Bibilioteca") -> None:
        """
        Sends an email
        
        :param to: Email address to send the message
        :param body: Body of the email. Can be an html code
        :param subject (default=biblioteca): Subject of the email
        """
        message = MIMEMultipart()
        message['From'] = Email.SENDER
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
            
        await to_thread(lambda: Email.SERVER.sendmail(
            Email.SENDER,
            to,
            message.as_string()
        ))
    