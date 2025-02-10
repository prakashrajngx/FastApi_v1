from pydantic import BaseModel, Field
from typing import Any, Optional

class webaddress(BaseModel):
    addressId: Optional[str] = None  # Define _id field explicitly
    emailID: Optional[str] = None
    landmark:Optional[str] =None 
    city:Optional[str]=None
    state:Optional[str]=None
    country:Optional[str]=None
    phoneNumber1: Optional[Any] = None
    phoneNumber2: Optional[Any] = None
   
 
class webaddressPost(BaseModel):
    emailID: Optional[str] = None
    landmark:Optional[str] =None 
    city:Optional[str]=None
    state:Optional[str]=None
    country:Optional[str]=None
    phoneNumber1: Optional[Any] = None
    phoneNumber2: Optional[Any] = None

   