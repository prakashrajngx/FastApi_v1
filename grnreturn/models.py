from pydantic import BaseModel, Field
from typing import List, Optional, Union
from fastapi import FastAPI

app = FastAPI()

# Define the ItemDetail model
class Item(BaseModel):
    itemId: Optional[str] = None
    itemName: Optional[str] = None
    quantity: Optional[float] = None
    returnQuantity: Optional[float] = None
    purchasetaxName:Optional[float] = None
    uom: Optional[str] = None
    unitPrice: Optional[float] = None
    sgst: Optional[float] = None
    cgst: Optional[float] = None
    barcode: Optional[str] = None
    discount:Optional[float] = None
    totalPrice: Optional[float] = None
    status: Optional[str] = None

# Define the GRN Return model
class GrnReturn(BaseModel):
    grnReturnId: Optional[str] = None
    grnId: Optional[str] = None
    vendorName: Optional[str] = None
    returnDate: Optional[str] = None
    returnLocation: Optional[str] = None
    itemDetails: Optional[List[Item]] = None
    receivedBy: Optional[str] = None
    totalReturnAmount: Optional[float] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    status: Optional[str] = None
    randomId:Optional[str] = None

# Define the GRN Return model
class GrnReturnPost(BaseModel):
    grnId: Optional[str] = None
    vendorName: Optional[str] = None
    returnDate: Optional[str] = None
    returnLocation: Optional[str] = None
    itemDetails: Optional[List[Item]] = None
    receivedBy: Optional[str] = None
    totalReturnAmount: Optional[float] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    status: Optional[str] = None
    randomId:Optional[str] = None