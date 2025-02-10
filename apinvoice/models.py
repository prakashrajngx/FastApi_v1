from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional, Union
from fastapi import FastAPI

app = FastAPI()

# Define the ItemDetail model
class ItemDetail(BaseModel):
    itemId: Optional[str] = None
    itemName: Optional[str] = None
    nos: Optional[float]  =None
    purchasecategoryName:Optional[str]=None
    purchasesubcategoryName: Optional[Any] = None
    eachQuantity:  Optional[float]  =None
    quantity: Optional[float]  =None
    uom:Optional[str] =None
    befTaxDiscount:Optional[float] = None
    afTaxDiscount:Optional[float] = None
    befTaxDiscountAmount:Optional[float] = None
    afTaxDiscountAmount:Optional[float] = None
    purchasetaxName:Optional[float] = None
    stockQuantity: Optional[float] = None
    unitPrice: Optional[float] = None
    totalPrice: Optional[float] = None
    taxType: Optional[Literal["cgst_sgst", "igst"]] = None
    sgst: Optional[float] = None
    cgst: Optional[float] = None
    igst: Optional[float] = None
    status: Optional[str] = None
    discountAmount: Optional[float] =None
    taxAmount: Optional[float] =None
    finalPrice: Optional[float] = None
    
# Define the GRN model
class Apinvoice(BaseModel):
    invoiceId: Optional[str] = None
    purchaseOrderId: Optional[str] = None
    grnId:Optional[str] = None
    vendorName: Optional[str] = None
    apinvoiceDate: Optional[datetime] = None
    invoiceDate: Optional[datetime] =None
    grnDate:Optional[datetime]=None
    invoiceNo:Optional[str] =None
    poDate: Optional[datetime] =None
    dueDate: Optional[datetime] = None
    itemDetails: Optional[List[ItemDetail]] = None
    invoiceAmount: Optional[float] = None
    taxDetails: Optional[float] = None
    discountDetails: Optional[float] = None
    discountPrice: Optional[float] = None
    apDiscountPrice:Optional[float] =None
    paymentTerms: Optional[str] = None
    paymentStatus: Optional[str] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[datetime] = None
    lastUpdatedDate:Optional[datetime] = None
    contactpersonEmail: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[int] = None
    gstNumber: Optional[str] = None
    paymentTerms: Optional[str] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    randomId:Optional[str] = None   
    status:Optional[str]= None

class ApinvoicePost(BaseModel):
    purchaseOrderId: Optional[str] = None
    grnId:Optional[str] = None
    vendorName: Optional[str] = None
    apinvoiceDate: Optional[datetime] = None
    poDate: Optional[datetime] =None
    invoiceDate: Optional[datetime] =None
    invoiceNo:Optional[str] =None
    dueDate: Optional[datetime] = None
    grnDate:Optional[datetime] =None
    itemDetails: Optional[List[ItemDetail]] = None
    invoiceAmount: Optional[float] = None
    taxDetails: Optional[float] = None
    discountDetails: Optional[float] = None
    discountPrice: Optional[float] = None
    apDiscountPrice:Optional[float] =None
    paymentTerms: Optional[str] = None
    paymentStatus: Optional[str] = None
    comments: Optional[str] = None
    attachments: Optional[Union[str, None]] = None
    createdDate: Optional[datetime] = None
    lastUpdatedDate:Optional[datetime] = None
    contactpersonEmail: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[int] = None
    gstNumber: Optional[str] = None
    paymentTerms: Optional[str] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    randomId:Optional[str] = None
    status:Optional[str]= None

