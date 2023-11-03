"""
# apibiblioteca.email

This module contains the Email class, that have a function to send emails asynchronously.
"""

from asyncio import to_thread
from .utils import SERVER, EMAIL_SENDER
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Email:
    """
    # apibiblioteca.email.Email
    
    This class contains constants associated to the method used for sendind
    """
    
    SERVER = SERVER
    
    async def message(to: str, body: str, subject: str="Bibilioteca") -> None:
        """
        Sends an email
        
        :param to: Email address to send the message
        :param body: Body of the email. Can be an html code
        :param subject (default=biblioteca): Subject of the email
        """
        message = MIMEMultipart()
        message['From'] = EMAIL_SENDER
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
            
        await to_thread(lambda: Email.SERVER.sendmail(
            EMAIL_SENDER,
            to,
            message.as_string()
        ))
    