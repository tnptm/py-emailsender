# Copyright (c) 2025 Toni Patama
# This code is licensed under the MIT License.
# See the LICENSE file for details.


from pydantic import BaseModel, EmailStr, ValidationError, Field
from typing import Sequence


class EmailList(BaseModel):
    emails: Sequence[EmailStr]



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
        