from pydantic import BaseModel, EmailStr, ValidationError, Field
from typing import Sequence, Optional, List


class EmailList(BaseModel):
    emails: Sequence[EmailStr]


class Email:
    def __init__(self, email_string: str):
        self.email_str = email_string
        self.emails_raw: Sequence[str] = self._split_emails(email_string)
        self.emails_validated: Optional[EmailList] = None
        self.formatted: Optional[str] = None
        
    @staticmethod
    def _split_emails(email_string: str) -> Sequence[str]:
        return [email.strip() for email in email_string.split(',') if email.strip()]

    def validate(self) -> bool:
        try:
            self.emails_validated = EmailList(emails=self.emails_raw)
            formatted = ', '.join(str(email) for email in self.emails_validated.emails)
            print(f"Valid emails: {formatted}")
            return True
        except ValidationError as e:
            print("Validation error:", e)
            return False

# shorter and pydantic way to do it
 

class Emails(BaseModel):
    """Data model for a list of email addresses."""
    emails: Sequence[EmailStr] = Field(..., description="List of valid email addresses.")

def validate_receivers(receivers: str) -> Emails | None:
    
    try:
        final_receivers = Emails(emails=[email.strip() for email in receivers.split(',')])
        return final_receivers
    except ValidationError as e:
        print(f"INPUT: {receivers}, ERROR: {e}")
        return None
        