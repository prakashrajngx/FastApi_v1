from pydantic import BaseModel, Field
from typing import Optional, List

class ItemType(BaseModel):
    itemtransferId: Optional[str] = None  
    itemCode: Optional[List[str]] = None
    itemName: Optional[List[str]] = None
    reqQty: Optional[List[int]] = None
    approvedQty: Optional[List[int]] = None
    receivedQty: Optional[List[int]] = None
    sendQty: Optional[List[int]] = None
    fromBranch: Optional[str] = None
    toBranch: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = None

class ItemTypePost(BaseModel):
    itemCode: Optional[List[str]] = None
    itemName: Optional[List[str]] = None
    reqQty: Optional[List[int]] = None
    approvedQty: Optional[List[int]] = None
    receivedQty: Optional[List[int]] = None
    sendQty: Optional[List[int]] = None
    fromBranch: Optional[str] = None
    toBranch: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = None
    