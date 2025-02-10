from pydantic import BaseModel, Field
from typing import List, Optional

class addOn(BaseModel):
    addOnId: Optional[str] = None
    addOn: Optional[str] = None
    addOnItems: Optional[List[str]] = None  # Make this field optional
    value: Optional[int] = None
    status: Optional[str] = None
    randomId: Optional[str] = None

class addOnPost(BaseModel):
    addOn: Optional[str] = None
    addOnItems: Optional[List[str]] = None  # Make this field optional if necessary
    value: Optional[int] = None
    status: Optional[str] = None
