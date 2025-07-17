"""
FastAPI web application for sending emails.

This module provides a simple web interface to send emails.
It defines two endpoints:
- GET /email: Displays an HTML form for composing an email.
- POST /send: Handles the form submission to send the email using credentials
              loaded from a .env file.
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from dotenv import load_dotenv
import os

from .utils.email import EmailSender, EmailData, EmailAccount
from .utils.validation_classes import validate_receivers
from typing_extensions import Annotated
#from pydantic import ValidationError

app = FastAPI()

load_dotenv()
templates = Jinja2Templates(directory="templates")


email_account = EmailAccount(
    password = os.getenv('EMAIL_PASSWORD'),
    username = os.getenv('EMAIL_USERNAME'),
    smtp_server = os.getenv('EMAIL_SMTP_SERVER'),
    smtp_port = os.getenv('EMAIL_SMTP_PORT')
)

@app.post('/send')
async def send_email( request: Request,
               title: Annotated[str, Form()],
               body: Annotated[str, Form()],
               sender: Annotated[str, Form()],
               receivers: Annotated[str, Form()],
               reply_to: Annotated[str | None, Form()] = None) -> HTMLResponse:
    """from email form, receive data and send email"""
    # Pydantic's EmailStr doesn't accept empty strings, so convert to None if empty.
    final_reply_to = reply_to if reply_to else None

    final_receivers = None
    final_receivers = [ email_addr.strip() for email_addr in receivers.split(',')] #if ',' in receiver else receiver
    

    
    # validate receivers
    final_receivers = validate_receivers(receivers)
    if final_receivers == None:
        # if validation fails, return error message
        return templates.TemplateResponse("email.html", context={ "request": request, 
                                                                "sent": False, 
                                                                "message": "Invalid email addresses."})
    #else:    
    #    return templates.TemplateResponse("email.html", context={ "request": request, 
    #                                                    "sent": False, 
    #                                                    "message": "Invalid email addresses."})
    # email sending code begins and ends to ".send()"
    email_data = EmailData(
        title=title,
        body=body,
        sender=sender,
        receivers=final_receivers,
        reply_to=final_reply_to
    )
    #print(f"Email Data: {email_data}")
    sender = EmailSender(
        email_data=email_data, 
        email_account=email_account
    )
    # Send
    result = sender.send()

    # return result
    return templates.TemplateResponse("email.html", context={ "request": request, 
                                                      "sent": result.sent, 
                                                      "message": result.message})


# create email sender form template
@app.get('/email')
async def email_form(request: Request):
    # read email.html template and show it

    return templates.TemplateResponse("email.html", {"request": request})


