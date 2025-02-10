from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class webpromotionalcard(BaseModel):
    detailid: Optional[str] = Field(alias="_id")  # Map to MongoDB's _id
    heading: Optional[str] = None
    paragraph: Optional[str] = None



class webpromotionalcardpost(BaseModel):
    heading: Optional[str] = None
    paragraph: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True  # Allows MongoDB's ObjectId to be used without issues
