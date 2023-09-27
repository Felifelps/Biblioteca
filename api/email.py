"""
# api.email

This module contains the Email class, that have a function to send emails asynchronously.
"""

from asyncio import to_thread
from api.connector import Connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

class Email:
    """
    # api.email.Email
    
    This class contains constants and associated to the method used for sendind
    """
    
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SENDER = 'mestount@gmail.com'
    PASSWORD = 'iquduhyskpuadboe'
    SERVER = SMTP(SMTP_SERVER, SMTP_PORT)
    SERVER.starttls()
    SERVER.login(SENDER, PASSWORD)
    
    
    @Connector.catch_error
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
        
