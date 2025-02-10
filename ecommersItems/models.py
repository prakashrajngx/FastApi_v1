from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class webitems(BaseModel):
    itemid: Optional[str] = Field(alias="_id")  # Map to MongoDB's _id
    category: Optional[str] = None
    variancename: Optional[str] = None
    webitemname: Optional[str] = None
    price: Optional[float] = None
    strickprice:Optional[float]=None  # Use float for price
    tax: Optional[float] = None  # Use float for tax
    uom: Optional[str] = None
    gram:Optional[float]=None

   
class webitemspost(BaseModel):
    category: Optional[str] = None
    variancename: Optional[str] = None
    webitemname: Optional[str] = None
    price: Optional[float] = None  # Use float for price
    strickprice  :Optional[float]=None 
    tax: Optional[float] = None  # Use float for tax
    uom: Optional[str] = None
    gram:Optional[float]=None

    class Config:
        arbitrary_types_allowed = True  # Allows MongoDB's ObjectId to be used without issues


