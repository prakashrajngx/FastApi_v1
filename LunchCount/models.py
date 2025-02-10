from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Lunch(BaseModel):
    branch:Optional[str] =None
    date:Optional[datetime]= Field(default_factory=datetime.now)
    lunchCount:Optional[float] =None
    employee:Optional[float]=None

class LunchGet(Lunch):
    id:str  