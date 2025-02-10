from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union


class CompanyStatus(BaseModel):
    companyStatusId: Optional[str] = None
    companyStatus: Optional[str] = None
    status: Optional[str] = None

class CompanyStatusPost(BaseModel):
    companyStatus: Optional[Union[str, int]] = None
    status: Optional[str] = None