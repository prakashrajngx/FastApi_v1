from pydantic import BaseModel, Field
from typing import Optional

class uom(BaseModel):
    uomId: Optional[str] = None  # Define _id field explicitly
    uom: Optional[str] = None
    precision: Optional[str] = None
    status: Optional[str] = None
    randomId: Optional[str] = None
class uomPost(BaseModel):
    uom: Optional[str] = None
    precision: Optional[str] = None
    status: Optional[str] = None