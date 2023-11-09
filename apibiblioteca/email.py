"""
# apibiblioteca.email

This module contains the Email class, that have a function to send emails asynchronously.
"""

from asyncio import to_thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from .utils import EMAIL_SENDER, EMAIL_PASSWORD
from threading import Thread

print('[CONNECTING TO SMTP SERVER]')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SERVER = SMTP(SMTP_SERVER, SMTP_PORT)
SERVER.starttls()
SERVER.login(EMAIL_SENDER, EMAIL_PASSWORD)
print('[CONNECTED TO SMTP SERVER]')

class Email:
    """
    # apibiblioteca.email.Email
    
    This class contains constants associated to the method used for sendind
    """
    
    async def message(to: str, body: str, subject: str="Bibilioteca") -> None:
        """
        Sends an email
        
        :param to: Email address to send the message
        :param body: Body of the email. Can be an html code
        :param subject (default=biblioteca): Subject of the email
        """
        
        SERVER = SMTP(SMTP_SERVER, SMTP_PORT)
        SERVER.starttls()
        SERVER.login(EMAIL_SENDER, EMAIL_PASSWORD)
        message = MIMEMultipart()
        message['From'] = EMAIL_SENDER
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
            
        Thread(target=lambda: SERVER.sendmail(
            EMAIL_SENDER,
            to,
            message.as_string()
        )).start()
    