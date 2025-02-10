from pydantic import BaseModel
from typing import List, Optional

# Variance Model
class Variant(BaseModel):
    kg: str
    
    price: Optional[int] = None  # Optional
    qrcode: Optional[str] = None   # Optional
    offer: Optional[int] = None    # Optional


# Birthday Cake Item Model
class BirthdayCakeItem(BaseModel):
    birthdayCakeId: Optional[str] = None
    category: Optional[str] = None
    appItemName: Optional[str] = None
    name: Optional[str] = None
    flavour: Optional[str] = None
    tax: Optional[int] = None  # Optional
    # netPrice: Optional[int] = None  # Optional
    finalPrice: Optional[int] = None  # Optional
    # uom: str
    hsnCode: Optional[int] = None  # Optional
    type: Optional[str] = None
    description: Optional[str] = None
    stockQuantity: Optional[int] = None # Optional
    offer: Optional[int] = None # Optional
    variances: Optional[List[Variant]] = []
    status: Optional[str] = None




# Model for POST requests

class BirthdayCakeItemPost(BaseModel):
    
    itemCode: Optional[str] = None
    category: Optional[str] = None
    appItemName: Optional[str] = None
    name: Optional[str] = None
    variant: Optional[int] = None
    flavour: Optional[str] = None
    tax: Optional[int] = None  # Optional
    # netPrice: Optional[int] = None  # Optional
    finalPrice: Optional[int] = None  # Optional
    # uom: str
    hsnCode: Optional[int] = None  # Optional
    type: Optional[str] = None
    description: Optional[str] = None
    stockQuantity: Optional[int] = None # Optional
    offer: Optional[int] = None # Optional
    variances: Optional[List[Variant]] = []
    status: Optional[str] = None

