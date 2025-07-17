"""
Email sending classes: wrapper for smtplib

The email.py module provides a set of classes to simplify sending emails using 
Python's smtplib library. It uses Pydantic for data validation and provides an 
object-oriented approach to email creation and sending.

"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from pydantic import BaseModel, EmailStr
from typing import Sequence




class EmailData(BaseModel):
    title: str
    body: str
    sender: EmailStr
    receivers: str | Sequence[str]
    reply_to: EmailStr | None = None

class EmailAccount(BaseModel):
    password: str
    username: str
    smtp_server: str
    smtp_port: str


class SendResult(BaseModel):
    message: str
    sent: bool

class EmailSender:
    mime_message: MIMEMultipart
    
    def __init__(self, email_data: EmailData, email_account: EmailAccount):
        self.email_data = email_data
        self.email_account = email_account

        
    def create_email_mime(self) -> None:
        """Create MIME message from email data."""
        if isinstance(self.email_data.receivers, str):
            self.email_data.receivers = [self.email_data.receivers]

        # Create MIME message
        message = MIMEMultipart()
        message["From"] = self.email_data.sender
        message["To"] = ", ".join(self.email_data.receivers) # compatible with several to addresses
        message["Subject"] = self.email_data.title
        message["Date"] = formatdate(localtime=True)
        if self.email_data.reply_to:
            print(f"Reply-To: {self.email_data.reply_to}")
            message["Reply-To"] = self.email_data.reply_to

        # Add body to email
        body = self.email_data.body
        message.attach(MIMEText(body, "plain"))
        self.mime_message = message
        

    def send(self) -> SendResult:
        """Create secure SSL context if smtp port is 465 and sends email"""
        context = ssl.create_default_context()
        result: SendResult = None
        smtp_port = int(self.email_account.smtp_port)
        try:
            # SMTP_SSL
            if smtp_port == 465:
                with smtplib.SMTP_SSL(self.email_account.smtp_server, smtp_port, context=context) as server:
                    server.login(self.email_account.username, self.email_account.password)
                    server.sendmail(from_addr=self.email_data.sender, to_addrs=self.email_data.receivers, msg=self.mime_message.as_string())
            # SMTP (25,587)
            elif smtp_port == 25 or smtp_port == 587:
                with smtplib.SMTP(self.email_account.smtp_server, smtp_port) as server:
                    if smtp_port == 587:
                        server.starttls(context=context)
                    server.login(self.email_account.username, self.email_account.password)
                    server.sendmail(from_addr=self.email_data.sender, to_addrs=self.email_data.receivers, msg=self.mime_message.as_string())
            print(f"Email sent successfully to {self.email_data.receivers}.")    
            result = SendResult(
                message = f"Email sent successfully to {self.email_data.receivers}.",
                sent = True
            )

        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")
            result = SendResult(
                message = f"Error sending email: {e}",
                sent = False
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            result = SendResult(
                message = f"Error sending email: {e}",
                sent = False
            )
        return result
