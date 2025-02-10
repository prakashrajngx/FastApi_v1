from pydantic import BaseModel, Field
from typing import Optional

class DeviceCode(BaseModel):
    deviceCodeId: Optional[str] = None
    deviceCode: Optional[str] = None
    deviceName: Optional[str] = None
    assetName: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    status: Optional[str] = None
    randomId: Optional[str] = None
    
class DeviceCodePost(BaseModel):
     deviceCode: Optional[str] = None
     status: Optional[str] = None
     branchId: Optional[str] = None
     deviceName: Optional[str] = None
     branchName: Optional[str] = None
     assetName: Optional[str] = None
     
class DeviceCodePatch(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None