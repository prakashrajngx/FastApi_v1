from pydantic import BaseModel, Field
from typing import List, Optional

class ConfigItem(BaseModel):
    varianceName:str
    weight: Optional[float] = None
    configQty: List[int]
    addOn: List[List[str]]
    addOnPrice: List[List[int]]
    variance: List[str]
    type: List[str]
    remark:List[str]
    
class Diningorder(BaseModel):
    orderId: Optional[str] = None
    itemNames: List[str]  
    varianceNames: List[str]
    prices: List[float]
    weights: List[float]
    quantities: List[float]
    amounts: List[float]
    taxes: List[float]
    uoms: List[str]
    totalAmount: Optional[float] = None
    status: Optional[str] = None
    orderType: Optional[str] = None
    tokenNo: Optional[int] = None
    branchName: Optional[str] = None
    table: Optional[str] = None
    seat: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    
    preinvoiceTime: Optional[str] = None
    waiter: Optional[str] = None
    deviceId: Optional[str] = None
    pax: Optional[str] = None
    hiveOrderId: Optional[str] = None
    seathiveOrderId: Optional[str] = None
    cancelledQty: List[float]  # No null values allowed
    orderRemark: Optional[str] = None
    itemRemark: List[str]
    partiallyCancelled: Optional[str] = None
    config: List[ConfigItem]  # Updated to List[ConfigItem]


class DiningorderCreate(BaseModel):
    itemNames: List[str]  # No null values allowed in the list
    varianceNames: List[str]
    prices: List[float]
    weights: List[float]
    quantities: List[float]
    amounts: List[float]
    taxes: List[float]
    uoms: List[str]
    totalAmount: Optional[float] = None
    status: Optional[str] = None
    orderType: Optional[str] = None
    tokenNo: Optional[int] = None
    branchName: Optional[str] = None
    table: Optional[str] = None
    seat: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    
    preinvoiceTime: Optional[str] = None
    waiter: Optional[str] = None
    deviceId: Optional[str] = None
    pax: Optional[str] = None
    hiveOrderId: Optional[str] = None
    seathiveOrderId: Optional[str] = None
    cancelledQty: List[float]  # No null values allowed
    orderRemark: Optional[str] = None
    itemRemark: List[str]
    partiallyCancelled: Optional[str] = None
    config: List[ConfigItem]  # Updated to List[ConfigItem]


class DiningorderUpdate(BaseModel):
    itemNames: List[str]  # No null values allowed in the list
    varianceNames: List[str]
    prices: List[float]
    weights: List[float]
    quantities: List[float]
    amounts: List[float]
    taxes: List[float]
    uoms: List[str]
    totalAmount: Optional[float] = None
    status: Optional[str] = None
    orderType: Optional[str] = None
    tokenNo: Optional[int] = None
    branchName: Optional[str] = None
    table: Optional[str] = None
    seat: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None

    preinvoiceTime: Optional[str] = None
    waiter: Optional[str] = None
    deviceId: Optional[str] = None
    pax: Optional[str] = None
    hiveOrderId: Optional[str] = None
    seathiveOrderId: Optional[str] = None
    cancelledQty: List[float]  # No null values allowed
    orderRemark: Optional[str] = None
    itemRemark: List[str]
    partiallyCancelled: Optional[str] = None
    config: List[ConfigItem]  # Updated to List[ConfigItem]

