from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Employee(BaseModel):
    empName:str
    date:Optional[datetime]= Field(default_factory=datetime.now)
    status: str = Field(default="active")
    branchId:Optional[str] =None
    branchName:Optional[str] =None
    
class EmployeeGet(Employee):
    id:str
