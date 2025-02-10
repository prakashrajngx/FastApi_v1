from pydantic import BaseModel, Field
from typing import Optional, List ,Any,Union

class Vehicle(BaseModel):
    id: Optional[str] = Field(None, alias="vehicleId")
    vehicleName: Optional[str] = None
    vehicleModel: Optional[str] = None
    vehicleNo: Optional[str] = None
    status: Optional[str]  = None


class VehiclePost(BaseModel):

    vehicleName: Optional[str] = None
    vehicleModel:  Optional[str] = None
    vehicleNo: Optional[str] = None
    status: Optional[Union[str, int]] = None
