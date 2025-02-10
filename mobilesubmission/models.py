from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Mobile(BaseModel):
  empName:Optional[str] =None
  date:Optional[datetime]= Field(default_factory=datetime.now)
  status: str = Field(default="active")
  branchId:Optional[str] =None
  branchName:Optional[str] =None

class MobileGet(Mobile):
  id:Optional[str] =None
 