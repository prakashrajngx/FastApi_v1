from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime, time

class SalesOrder(BaseModel):
    salesOrderId: Optional[str] = None
    itemName: Optional[List[str]] = None
    qty: Optional[List[int]] = None
    price: Optional[List[int]] = None
    itemCode: Optional[List[str]] = None   
    weight: Optional[List[float]] = None
    amount: Optional[List[float]] = None
    tax: Optional[List[int]] = None
    uom: Optional[List[str]] = None
    totalAmount: Optional[float] = None
    totalAmount2: Optional[float] = None
    netPrice: Optional[float] = None
    orderInvoiceNo: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    invoiceDate: Optional[str] = None
    cash: Optional[float] = None
    card: Optional[float] = None
    upi: Optional[float] = None
    deliveryPartners: Optional[str] = None
    otherPayments: Optional[float] = None
    deliveryPartnerName: Optional[str] = None
    shiftId: Optional[str] = None
    shiftName: Optional[str] = None
    user: Optional[str] = None   
    deliveryDate: Optional[datetime] = None
    deliveryTime: Optional[str] = None
    event: Optional[str] = None
    customerNumber: Optional[str] = None
    customerName: Optional[str] = None
    deliveryType: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    discount: Optional[int] = None
    discountAmount: Optional[float] = None
    remark: Optional[str] = None
    customCharge: Optional[float] = None
    advanceAmount:Optional[List[float]] = None
    advanceDateTime:Optional[List[datetime]] = None
    advancePaymentType:Optional[List[str]] = None
    paymentType: Optional[str] = None
    finalPrice: Optional[float] = None
    balanceAmount: Optional[float] = None
    saleOrderNo: Optional[str] = None
    orderDate: Optional[str] = None
    orderTime: Optional[str] = None
    employeeName: Optional[str] = None
    status: Optional[str] = None
    cancelOrderRemark: Optional[str] = None
    cancelOrderDate:Optional[datetime]=None
    returnAmount: Optional[str] = None
    approvedBy:Optional[str] = None
    canceledPersonName:Optional[str] = None
    canceledPaymentType:Optional[str]=None
    creditCustomerOrder:Optional[str] =None

def convert_to_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use dd-MM-yyyy."
        )  
class SalesOrderPost(BaseModel):
    itemName: Optional[list[str]] = None
    qty: Optional[list[int]] = None
    price: Optional[list[int]] = None
    itemCode: Optional[list[str]] = None   
    weight: Optional[list[float]] = None
    amount: Optional[list[float]] = None
    tax: Optional[list[int]] = None
    uom: Optional[list[str]] = None
    totalAmount: Optional[float] = None
    totalAmount2: Optional[float] = None
    netPrice: Optional[float] = None
    orderInvoiceNo: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    invoiceDate: Optional[str] = None
    cash: Optional[float] = None
    card: Optional[float] = None
    upi: Optional[float] = None
    deliveryPartners: Optional[str] = None
    otherPayments: Optional[float] = None
    deliveryPartnerName: Optional[str] = None
    shiftId: Optional[str] = None
    shiftName: Optional[str] = None
    user: Optional[str] = None   
    # deliveryDate: Optional[str] = None
    deliveryDate: Optional[str] = None 
    deliveryTime: Optional[str] = None 
    event: Optional[str] = None
    customerNumber:Optional[str] = None
    customerName: Optional[str] = None
    deliveryType: Optional[str] = None
    address: Optional[str] = None
    landmark: Optional[str] = None
    discount: Optional[int] = None
    discountAmount:Optional[float] = None
    remark: Optional[str] = None
    customCharge: Optional[float] = None
    advanceAmount:Optional[List[float]] = None
    advanceDateTime:Optional[List[datetime]] = None
    advancePaymentType:Optional[List[str]] = None
    paymentType: Optional[str] = None
    finalPrice: Optional[float] = None
    balanceAmount:Optional[float] = None
    saleOrderNo: Optional[str] = None
    orderDate: Optional[str] = None
    orderTime: Optional[str] = None
    employeeName:Optional[str] = None
    status: Optional[str] = None
    cancelOrderRemark: Optional[str] = None
    cancelOrderDate:Optional[datetime]=None
    returnAmount: Optional[str] = None
    approvedBy:Optional[str] = None
    canceledPersonName:Optional[str] = None
    canceledPaymentType:Optional[str] =None
    creditCustomerOrder:Optional[str] =None


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
    invoiceNo: Optional[str] = None
    deviceNumber: Optional[int] = None
    customCharge: Optional[int] = None
    discountAmount: Optional[float] = None
    discountPercentage: Optional[int] = None
    user: Optional[List[str]] = None
    deviceCode: Optional[str] = None
    creditCustomerOrder:Optional[str] =None


# class CancelOrder(BaseModel):
#     # cancelOrderId: Optional[str] = None
#     itemName: Optional[List[str]] = None
#     qty: Optional[List[int]] = None
#     price: Optional[List[int]] = None
#     itemCode: Optional[List[str]] = None   
#     weight: Optional[List[float]] = None
#     amount: Optional[List[float]] = None
#     tax: Optional[List[int]] = None
#     uom: Optional[List[str]] = None
#     totalAmount: Optional[float] = None
#     totalAmount2: Optional[float] = None
#     netPrice: Optional[float] = None
#     orderInvoiceNo: Optional[str] = None
#     branchId: Optional[str] = None
#     branchName: Optional[str] = None
#     invoiceDate: Optional[str] = None
#     cash: Optional[float] = None
#     card: Optional[float] = None
#     upi: Optional[float] = None
#     deliveryPartners: Optional[str] = None
#     otherPayments: Optional[float] = None
#     deliveryPartnerName: Optional[str] = None
#     shiftId: Optional[str] = None
#     shiftName: Optional[str] = None
#     user: Optional[str] = None   
#     deliveryDate: Optional[datetime] = None
#     deliveryTime: Optional[str] = None
#     event: Optional[str] = None
#     customerNumber: Optional[str] = None
#     customerName: Optional[str] = None
#     deliveryType: Optional[str] = None
#     address: Optional[str] = None
#     landmark: Optional[str] = None
#     discount: Optional[int] = None
#     discountAmount: Optional[float] = None
#     # remark: Optional[str] = None
#     customCharge: Optional[float] = None
#     advanceAmount: Optional[float] = None
#     paymentType: Optional[str] = None
#     finalPrice: Optional[float] = None
#     balanceAmount: Optional[float] = None
#     saleOrderNo: Optional[str] = None
#     orderDate: Optional[str] = None
#     orderTime: Optional[str] = None
#     employeeName: Optional[str] = None
#     status: Optional[str] = None
    
# # class CancelOrderPayload(BaseModel):
# #     cancelOrderRemark: Optional[str] = None
# #     approvedBy: Optional[str] = None
# #     employeeName: Optional[str] = None
# #     returnedAmount:  Optional[float] = None
# #     paymentType: Optional[str] = None

# class CancelOrderPayload(BaseModel):
#     cancelOrderRemark: Optional[str] = None
#     approvedBy: Optional[str] = None
#     employeeName: Optional[str] = None
#     returnedAmount: Optional[float] = None
#     paymentType: Optional[str] = None
#     status: Optional[str] = None  # To dynamically update the status of the sales order






