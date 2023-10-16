"""
# api.email

This module contains the Email class, that have a function to send emails asynchronously.
"""

from asyncio import to_thread
from .connector import Connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP, SMTPServerDisconnected

class Email:
    """
    # api.email.Email
    
    This class contains constants associated to the method used for sendind
    """
    
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER = Connector.EMAIL_SENDER
    PASSWORD = Connector.EMAIL_PASSWORD
    SERVER = SMTP(SMTP_SERVER, SMTP_PORT)
    SERVER.starttls()
    SERVER.login(SENDER, PASSWORD)
    
    def load_server(func):
        async def wrapper(*args, **kwargs):
            if Email.SERVER == None:
                Email.SERVER = await to_thread(SMTP(Email.SMTP_SERVER, Email.SMTP_PORT))
                await to_thread(Email.SERVER.starttls())
                await to_thread(Email.SERVER.login(Email.SENDER, Email.PASSWORD))
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
    
