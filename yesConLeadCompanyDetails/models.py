from pydantic import BaseModel, Field
from typing import Optional

class CompanyDetails(BaseModel):
    companyId: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    phone_number_1: Optional[str] = None
    phone_number_2: Optional[str] = None
    email_address: Optional[str] = None
    contact_name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None



class CompanyDetailsPost(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    phone_number_1: Optional[str] = None
    phone_number_2: Optional[str] = None
    email_address: Optional[str] = None
    contact_name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
