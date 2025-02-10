from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PaymentMethod(BaseModel):
    paymentId: Optional[str] = None  # Define _id field explicitly
    paymentMethod: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaymentMethodPost(BaseModel):
     paymentMethod: Optional[str] = None
     created_at: Optional[datetime] = None
     updated_at: Optional[datetime] = None

     