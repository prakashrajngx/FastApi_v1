from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union


class Issue(BaseModel):
    issueId: Optional[str] = None
    title: str  # Make customerId required
    status: Optional[str] = None

class IssuePost(BaseModel):
    title: Optional[Union[str, int]] = None
    status: Optional[str] = None
