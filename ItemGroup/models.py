from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ItemGroup(BaseModel):
    itemgroupId: Optional[str] = None  # Define _id field explicitly
    itemgroupName: Optional[str] = None
    createdDate:Optional[datetime] = None
    lastUpdatedDate:Optional[datetime] = None
    status: Optional[str] = None
    randomId: Optional[str] = None

class ItemGroupPost(BaseModel):
     itemgroupName: Optional[str] = None
     createdDate:Optional[datetime] = None
     lastUpdatedDate:Optional[datetime] = None
     status: Optional[str] = None