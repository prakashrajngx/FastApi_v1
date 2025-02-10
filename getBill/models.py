from pydantic import BaseModel, Field
from typing import Any, List, Optional,Union

from orders.models import ConfigItem

class Invoice(BaseModel):
    invoiceId: Optional[str] = None

    itemName: Optional[List[str]] = None
    varianceName: Optional[List[str]] = None
    price: Optional[List[float]] = None
    weight: Optional[List[float]] = None
    qty: Optional[List[int]] = None
    amount: Optional[List[float]] = None
    tax: Optional[List[float]] = None
    uom: Optional[List[str]] = None
    totalAmount: Optional[float] = None
    totalAmount2: Optional[float] = None
    totalAmount3: Optional[float] = None
    status: Optional[str] = None
    salesType: Optional[str] = None
    customerPhoneNumber: Optional[str] = "No Number"
    employeeName: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    paymentType: Optional[str] = None
    cash: Optional[int] = None
    card: Optional[int] = None
    upi: Optional[int] = None
    others: Optional[str] = None
    invoiceDate: Optional[str] = None
    invoiceTime: Optional[str] = None
    shiftNumber: Optional[int] = None
    shiftId: Optional[int] = None
    invoiceNo: Optional[Any] = None
    deviceNumber: Optional[int] = None
    customCharge: Optional[int] = None
    discountAmount: Optional[float] = None
    discountPercentage: Optional[int] = None
    user: Optional[List[str]] = None
    deviceCode:Optional[str]=None
    kotaddOns:Optional[List[ConfigItem]] = None
    
    
class InvoiceCreate(BaseModel):

    itemName: Optional[List[str]] = None
    varianceName: Optional[List[str]] = None
    price: Optional[List[float]] = None
    weight: Optional[List[float]] = None
    qty: Optional[List[int]] = None
    amount: Optional[List[float]] = None
    tax: Optional[List[float]] = None
    uom: Optional[List[str]] = None
    totalAmount: Optional[float] = None
    totalAmount2: Optional[float] = None
    totalAmount3: Optional[float] = None
    status: Optional[str] = None
    salesType: Optional[str] = None
    customerPhoneNumber: Optional[str] = "No Number"
    employeeName: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    paymentType: Optional[str] = None
    cash: Optional[int] = None
    card: Optional[int] = None
    upi: Optional[int] = None
    others: Optional[str] = None
    invoiceDate: Optional[str] = None
    invoiceTime: Optional[str] = None
    shiftNumber: Optional[int] = None
    shiftId: Optional[int] = None
    invoiceNo: Optional[Any] = None
    deviceNumber: Optional[int] = None
    customCharge: Optional[int] = None
    discountAmount: Optional[float] = None
    discountPercentage: Optional[int] = None
    user:Optional[List[str]] = None
    deviceCode:Optional[str]=None
    kotaddOns:Optional[List[ConfigItem]] = None
    
    
class InvoiceUpdate(BaseModel):

    itemName: Optional[List[str]] = None
    varianceName: Optional[List[str]] = None
    price: Optional[List[float]] = None
    weight: Optional[List[float]] = None
    qty: Optional[List[int]] = None
    amount: Optional[List[float]] = None
    tax: Optional[List[float]] = None
    uom: Optional[List[str]] = None
    totalAmount: Optional[float] = None
    totalAmount2: Optional[float] = None
    totalAmount3: Optional[float] = None
    status: Optional[str] = None
    salesType: Optional[str] = None
    customerPhoneNumber: Optional[str] = "No Number"
    employeeName: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    paymentType: Optional[str] = None
    cash: Optional[int] = None
    card: Optional[int] = None
    upi: Optional[int] = None
    others: Optional[str] = None
    invoiceDate: Optional[str] = None
    invoiceTime: Optional[str] = None
    shiftNumber: Optional[int] = None
    shiftId: Optional[int] = None
    invoiceNo: Optional[Any] = None
    deviceNumber: Optional[int] = None
    customCharge: Optional[int] = None
    discountAmount: Optional[float] = None
    discountPercentage: Optional[int] = None
    user: Optional[List[str]] = None
    deviceCode:Optional[str]=None
    kotaddOns:Optional[List[ConfigItem]] = None