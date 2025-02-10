from pydantic import BaseModel, Field
from typing import Optional, Union

class Company(BaseModel):
    companyId: Optional[Union[str, int]] = None
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    contactDetails: Optional[str] = None
    companymail: Optional[str] = None
    status: Optional[str] = None

class CompanyPost(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    contactDetails: Optional[str] = None
    companymail: Optional[str] = None
    status: Optional[str] = None
