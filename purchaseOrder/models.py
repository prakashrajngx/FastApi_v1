from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union,Any
from datetime import datetime
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Define the Item model
class Item(BaseModel):
    itemId: Optional[str] = None
    itemCode:Optional[str] = None
    itemName: Optional[str] = None
    quantity: Optional[float] = None
    purchasecategoryName:Optional[str]=None
    purchasesubcategoryName: Optional[Any] = None
    uom: Optional[str] = None
    count: Optional[float]  =None
    eachQuantity:  Optional[float]  =None
    receivedQuantity: Optional[float] = None
    damagedQuantity: Optional[float] = None
    taxPercentage: Optional[float] = None
    existingPrice:Optional[float] = None
    newPrice : Optional[float] = None
    sgst: Optional[float] = None
    cgst: Optional[float] = None
    igst: Optional[float] = None
    taxType: Optional[Literal["cgst_sgst", "igst"]] = None
    befTaxDiscount: Optional[float] = None
    afTaxDiscount: Optional[float] =None
    befTaxDiscountAmount: Optional[float] = None
    afTaxDiscountAmount: Optional[float] =None
    discountAmount: Optional[float] =None
    taxAmount: Optional[float] =None
    barcode: Optional[str] = None
    pendingCount: Optional[float] = None
    pendingQuantity:Optional[float] = None
    pendingTotalQuantity: Optional[float] = None
    pendingTaxAmount:Optional[float] = None
    pendingDiscountAmount:Optional[float]= None
    pendingSgst: Optional[float] = None
    pendingCgst: Optional[float] = None
    pendingIgst: Optional[float] = None
    pendingTotalPrice:Optional[float] = None
    pendingFinalPrice:Optional[float] = None
    pendingBefTaxDiscountAmount: Optional[float] = None
    pendingAfTaxDiscountAmount: Optional[float] =None
    totalPrice: Optional[float] = None
    finalPrice: Optional[float] = None
    hsnCode:Optional[str] = None
    poPhoto: Optional[str] = None
    status:Optional[str] =None
# Define the PurchaseOrderState model
class PurchaseOrderState(BaseModel):
    purchaseOrderId:  Optional[str] = None
    vendorName: Optional[str] = None
    vendorContact: Optional[str] = None
    orderDate: Optional[datetime] = None
    invoiceDate: Optional[datetime] =None
    invoiceNo: Optional[str] =None
    expectedDeliveryDate: Optional[datetime] = None
    poStatus: Optional[str] = None
    items: Optional[List[Item]] = None
    totalOrderAmount: Optional[float] = None  # Consider using float if it's a numeric value
    discountPrice:Optional[float] = None
    paymentTerms: Optional[str] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    totalDiscount: Optional[float] =None
    totalTax: Optional[float] =None
    comments: Optional[str] = None
    attachments: Optional[str] = None 
    createdDate:Optional[datetime] = None
    createdTime:Optional[datetime] = None
    lastUpdatedDate:Optional[datetime] = None
    lastUpdatedTime:Optional[datetime] = None
    randomId:Optional[str] = None
    imageUrl: Optional[List[Any]] = None  # New field for the image URL
    contactpersonEmail: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    termsandConditions:Optional[List[str]] = None
    postalCode: Optional[int] = None
    gstNumber: Optional[str] = None
    itemStatus: Optional[str] = None
    pendingOrderAmount:Optional[float]=None
    pendingDiscountAmount:Optional[float] = None
    pendingTaxAmount:Optional[float] = None
# Define the PurchaseOrderPost model for creating new purchase orders
class PurchaseOrderPost(BaseModel):
    vendorName: Optional[str] = None
    vendorContact: Optional[str] = None
    orderDate: Optional[datetime] = None
    invoiceDate: Optional[datetime] =None
    invoiceNo: Optional[str] =None
    expectedDeliveryDate: Optional[datetime] = None
    poStatus: Optional[str] = None
    items: Optional[List[Item]] = None
    totalOrderAmount: Optional[float] = None  # Consider using float if it's a numeric value
    discountPrice:Optional[float] = None
    paymentTerms: Optional[str] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    totalDiscount: Optional[float] =None
    totalTax: Optional[float] =None
    comments: Optional[str] = None
    attachments:Optional[str] = None 
    createdDate:Optional[datetime] = None
    createdTime:Optional[datetime] = None
    lastUpdatedDate:Optional[datetime] = None
    lastUpdatedTime:Optional[datetime] = None
    imageUrl: Optional[List[Any]] = None  # New field for the image URL
    contactpersonEmail: Optional[str] = None
    termsandConditions:Optional[List[str]] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[int] = None
    gstNumber: Optional[str] = None
    itemStatus: Optional[str] = None
    pendingOrderAmount:Optional[float]=None
    pendingDiscountAmount:Optional[float] = None
    pendingTaxAmount:Optional[float] = None