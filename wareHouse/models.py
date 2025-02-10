from pydantic import BaseModel, Field
from typing import Any, List, Optional


class WareHouse(BaseModel):
    wareHouseId: Optional[str] = None  # MongoDB ObjectId
    wareHouseName: Optional[str] = None
    aliasName: Optional[str] = None
    status: Optional[Any] = None
    randomId: Optional[str] = None
    address: Optional[Any] = None
    country: Optional[str] = None
    state: Optional[Any] = None
    city: Optional[str] = None
    postalCode: Optional[Any] = None
    phoneNumber: Optional[Any] = None
    email: Optional[str] = None
    latitude: Optional[Any] = None
    longitude: Optional[Any] = None
    description: Optional[str] = None
    openingHours: Optional[Any] = None
    managerName: Optional[str] = None
    managerContact: Optional[Any] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    createdBy: Optional[str] = None
    amount: Optional[List[float]] = None
    totalAmount: Optional[str] = None


class WareHousePost(BaseModel):
    wareHouseName: Optional[str] = None
    aliasName: Optional[str] = None
    status: Optional[str] = None
    randomId: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    description: Optional[str] = None
    openingHours: Optional[str] = None
    managerName: Optional[str] = None
    managerContact: Optional[str] = None
    createdDate: Optional[str] = None
    lastUpdatedDate: Optional[str] = None
    createdBy: Optional[str] = None
    amount: Optional[List[float]] = None
    totalAmount: Optional[str] = None
