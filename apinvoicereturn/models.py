from pydantic import BaseModel, Field
from typing import List, Optional, Union
from fastapi import FastAPI

app = FastAPI()

# Define the Item model
class Item(BaseModel):
    itemId: Optional[str] = None
    itemName: Optional[str] = None
    quantity: Optional[float]  =None
    uom:Optional[str] =None
    discount:Optional[float] = None
    purchasetaxName:Optional[float] = None
    stockQuantity: Optional[float] = None
    unitPrice: Optional[float] = None
    sgst: Optional[float] = None
    cgst: Optional[float] = None
    totalPrice: Optional[float] = None
    status: Optional[str] = None

# Define the GRN model
class Apinvoicereturn(BaseModel):
    reverseinvoiceId: Optional[str] = None
    invoiceId: Optional[str] = None
    vendorName: Optional[str] = None
    reverseDate: Optional[str] = None
    itemDetails: Optional[List[Item]] = None
    reasonforReverse: Optional[str] = None
    totalReversalAmount: Optional[float] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    randomId:Optional[str] = None
    status:Optional[str]= None

class ApinvoicereturnPost(BaseModel):
    invoiceId: Optional[str] = None
    vendorName: Optional[str] = None
    reverseDate: Optional[str] = None
    itemDetails: Optional[List[Item]] = None
    reasonforReverse: Optional[str] = None
    totalReversalAmount: Optional[float] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    randomId:Optional[str] = None
    status:Optional[str]= None


