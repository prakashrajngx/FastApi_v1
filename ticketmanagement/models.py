from pydantic import BaseModel, Field, validator
from typing import Any, Optional
from datetime import datetime

class Ticket(BaseModel):
    ticketId: str
    ticketNo: Optional[str] = None 
    date: Optional[str] = None  # Store formatted date string here
    name: Optional[str] = None
    empId: Optional[str] = None
    employee: Optional[str] = None
    issue: Optional[str] = None
    companyStatus: Optional[str] = None
    address: Optional[str] = None
    reportFrom: Optional[str] = None
    reportFor: Optional[str] = None
    contactDetails: Optional[str] = None
    pendingQuery: Optional[str] = None
    companymail: Optional[str] = None
    amcType: Optional[str] = None  # 'AMC' or 'NonAMC'
    progressTime: Optional[str] = None
    completeTime: Optional[str] = None
    totalTime: Optional[str] = None
    receiptImage: Optional[str] = None 
    esign: Optional[str] = None 
    status: Optional[str] = None

class TicketPost(BaseModel):
    ticketNo: Optional[str] = None
    date: Optional[Any] = None  # Store as datetime object
    name: Optional[str] = None
    empId: Optional[str] = None
    employee: Optional[str] = None
    issue: Optional[str] = None
    companyStatus: Optional[str] = None
    address: Optional[str] = None
    reportFrom: Optional[str] = None
    reportFor: Optional[str] = None
    contactDetails: Optional[str] = None
    pendingQuery: Optional[str] = None
    companymail: Optional[str] = None
    amcType: Optional[str] = None  # 'AMC' or 'NonAMC'
    progressTime: Optional[str] = None
    completeTime: Optional[str] = None
    totalTime: Optional[str] = None
    receiptImage: Optional[str] = None
    esign: Optional[str] = None  
    status: Optional[str] = None

    # Validator to format the date when loading the model
    @validator('date', pre=True, always=True)
    def format_date(cls, value: Optional[datetime]) -> Optional[str]:
        if isinstance(value, datetime):
            # Format the datetime object to 'DD/MM/YYYY - HH:MM AM/PM'
            return value.strftime('%d/%m/%Y - %I:%M %p')
        return value
