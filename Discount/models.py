from pydantic import BaseModel, Field
from typing import Optional

class discount(BaseModel):
    discountId: Optional[str] = None  # Define _id field explicitly
    discountName: Optional[str] = None
    discountPercentage: Optional[str] = None
    status: Optional[str] = None
    randomId: Optional[str] = None
class discountPost(BaseModel):
    discountName: Optional[str] = None
    discountPercentage: Optional[str] = None
    status: Optional[str] = None