from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import date, datetime

class Vendor(BaseModel):
    vendorId: Optional[str] = None  # Define _id field explicitly
    vendorName: Optional[str] = None
    contactpersonName: Optional[str] = None
    contactpersonPhone: Optional[str] = None
    contactpersonEmail: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    vendorType: Optional[str] = None
    gstNumber: Optional[str] = None
    paymentTerms: Optional[str] = None
    creditLimit: Optional[int] = None
    preferredpaymentMethod: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[int] = None
    bankName: Optional[str] = None
    accountNumber: Optional[int] = None 
    ifscCode: Optional[str] = None
    createdDate:Optional[datetime] = None
    updatedDate:Optional[datetime] = None
    randomId: Optional[str] =None

class VendorPost(BaseModel):
    vendorName: Optional[str] = None
    contactpersonName: Optional[str] = None
    contactpersonPhone: Optional[str] = None
    contactpersonEmail: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    vendorType: Optional[str] = None
    gstNumber: Optional[str] = None
    paymentTerms: Optional[str] = None
    creditLimit: Optional[int] = None
    preferredpaymentMethod: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[int] = None
    bankName: Optional[str] = None
    accountNumber: Optional[int] = None 
    ifscCode: Optional[str] = None
    createdDate:Optional[datetime] = None
    updatedDate:Optional[datetime] = None
    randomId: Optional[str] = None   
 