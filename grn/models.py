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
    purchasetaxName:Optional[float] = None
    receivedQuantity: Optional[float] = None
    damagedQuantity: Optional[float] = None
    unitPrice: Optional[float] = None
    befTaxDiscount: Optional[float] = None
    afTaxDiscount: Optional[float] =None
    befTaxDiscountAmount: Optional[float] = None
    afTaxDiscountAmount: Optional[float] =None
    discount:Optional[float] = None
    discountAmount: Optional[float] =None
    taxAmount: Optional[float] =None
    totalPrice: Optional[float] = None
    taxType: Optional[Literal["cgst_sgst", "igst"]] = None
    sgst: Optional[float] = None
    cgst: Optional[float] = None
    igst: Optional[float] = None
    status: Optional[str] = None
    barcode: Optional[str] = None
    expiryDate: Optional[datetime] = None
    finalPrice: Optional[float] = None
# Define the GRN model
class Grn(BaseModel):
    grnId: Optional[str] = None
    purchaseOrderId: Optional[str] = None
    vendorName: Optional[str] = None
    grnDate: Optional[datetime] = None
    agingDay: Optional[int] = None
    poDate: Optional[datetime] =None
    invoiceDate: Optional[datetime] =None
    invoiceNo:Optional[str] =None
    receivingLocation: Optional[str] = None
    itemDetails: Optional[List[ItemDetail]] = None
    inspectionStatus: Optional[str] = None
    receivedBy: Optional[str] = None
    totalReceivedAmount: Optional[float] = None
    totalDiscount: Optional[float] =None
    totalTax: Optional[float] =None
    discountPrice: Optional[float] =None
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
    paymentTerms: Optional[str] = None
    gstNumber: Optional[str] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    status: Optional[str] = None
    randomId:Optional[str] = None
    

class GrnPost(BaseModel):
    vendorName: Optional[str] = None
    purchaseOrderId: Optional[str] = None
    grnDate: Optional[datetime] = None
    agingDay: Optional[int] = None
    poDate: Optional[datetime] =None
    invoiceDate: Optional[datetime] =None
    invoiceNo:Optional[str] =None
    receivingLocation: Optional[str] = None
    itemDetails: Optional[List[ItemDetail]] = None
    inspectionStatus: Optional[str] = None
    receivedBy: Optional[str] = None
    totalDiscount: Optional[float] =None
    totalTax: Optional[float] =None
    discountPrice: Optional[float] =None
    totalReceivedAmount: Optional[float] = None
    comments: Optional[str] = None
    paymentTerms: Optional[str] = None    
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
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    status: Optional[str] = None
    randomId:Optional[str] = None

