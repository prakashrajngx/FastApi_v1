from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

class Item(BaseModel):
    item_name: Optional[str] = None  
    uom: Optional[str] = None  
    grams: Optional[float] =None

class MixBox(BaseModel):
    id: Optional[str] = None  # Define _id field explicitly
    mixboxName: Optional[str] = None  
    totalGrams: Optional[float] =None
    items: List[Item] =None
    status: Optional[int] = 1  # Default to active


class MixBoxPost(BaseModel):
    mixboxName: Optional[str] = None  # Define _id field explicitly
    totalGrams: Optional[float] =None
    items: List[Item] =None
    status: Optional[int] = 1  # Default to active
