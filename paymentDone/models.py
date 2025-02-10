from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from fastapi import FastAPI

app = FastAPI()


class PaymentDone(BaseModel):
    paymentDoneId:Optional[str] = None
    outgoingIds: List[str]  # List of outgoing IDs
    invoiceDate: List[str]
    invoiceNo: List[str]
    vendorName: List[str]
    totalPayableAmount: List[float]
    fullPaymentAmount: List[float]
    paymentType: Optional[str] = None 
    cashVoucherNo: Optional[str] = None  
    chequeNo: Optional[float] = None 
    neftNo: Optional[float] = None  
    rtgsNo: Optional[float] = None  
    totalPaymentAmount:Optional[float] = None
    onlinePayment: Optional[float] = None  
    status: Optional[str] = None

class PaymentDonePost(BaseModel):
    outgoingIds: List[str]  # List of outgoing IDs
    invoiceDate: List[str]
    invoiceNo: List[str]
    vendorName: List[str]
    totalPayableAmount: List[float]
    fullPaymentAmount: List[float]
    paymentType: Optional[str] = None 
    cashVoucherNo: Optional[str] = None  
    chequeNo: Optional[float] = None 
    neftNo: Optional[float] = None  
    rtgsNo: Optional[float] = None  
    totalPaymentAmount:Optional[float] = None
    onlinePayment: Optional[float] = None  
    status: Optional[str] = None
