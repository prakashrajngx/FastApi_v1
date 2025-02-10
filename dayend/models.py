from pydantic import BaseModel, Field
from typing import Any, Optional, Union

class Shift(BaseModel):
    shiftId: Optional[str] = Field(None, alias="shiftId")
    shiftNumber: Optional[Union[str, int]] = None
    shiftOpeningDate: Optional[str] = None
    shiftOpeningTime: Optional[str] = None
    shiftClosingDate: Optional[str] = None
    shiftClosingTime: Optional[str] = None
    systemOpeningBalance: Optional[str] = None
    manualOpeningBalance: Optional[str] = None
    systemClosingBalance: Optional[str] = None
    manualClosingBalance: Optional[str] = None
    openingDifferenceAmount: Optional[str] = None
    openingDifferenceType: Optional[str] = None
    closingDifferenceAmount: Optional[str] = None
    closingDifferenceType: Optional[str] = None
    cashSales: Optional[str] = None
    cardSales: Optional[str] = None
    upiSales: Optional[str] = None
    deliveryPartnerSales: Optional[str] = None
    otherSales: Optional[str] = None
    salesReturn: Optional[str] = None
    dayendStatus: Optional[str] = None
    status: Optional[str] = None
    branchId: Optional[str] = None
    branchName: Optional[str] = None
    shiftOpenId: Optional[str] = None
    shiftOpenName: Optional[str] = None
    deviceId: Optional[str] = None
    deviceNumber: Optional[str] = None
    manualCashsales:Optional[Any]=None
    manualUpisales:Optional[Any]=None
    manualCardsales:Optional[Any]=None
    manualDeliverypartnersales:Optional[Any]=None
    manualOthersales:Optional[Any]=None
class ShiftPost(BaseModel):

    shiftNumber: Optional[Union[str, int]] = None
    shiftOpeningDate: Optional[str] = None
    shiftOpeningTime: Optional[str] = None
    shiftClosingDate: Optional[str] =  None
    shiftClosingTime: Optional[str] =  None
    systemOpeningBalance: Optional[Union[str, int]] = None
    manualOpeningBalance: Optional[Union[str, int]] = None
    systemClosingBalance: Optional[Union[str, int]] = None
    manualClosingBalance: Optional[Union[str, int]] = None
    openingDifferenceAmount: Optional[Union[str, int]] = None
    openingDifferenceType: Optional[str] = None
    closingDifferenceAmount:Optional[Union[str, int]] = None
    closingDifferenceType: Optional[str] = None
    cashSales: Optional[Union[str, int]] = None
    cardSales: Optional[Union[str, int]] = None
    upiSales: Optional[Union[str, int]] =  None    
    deliveryPartnerSales: Optional[Union[str, int]] = None
    otherSales: Optional[Union[str, int]] = None
    salesReturn: Optional[str] = None
    dayendStatus: Optional[str] = None
    status:Optional[str] = None
    branchId: Optional[Union[str, int]] = None
    branchName: Optional[str] = None
    shiftOpenId: Optional[Union[str, int]] = None
    shiftOpenName: Optional[str] = None
    deviceId: Optional[Union[str, int]] = None
    deviceNumber: Optional[Union[str, int]] = None
    manualCashsales:Optional[Any]=None
    manualUpisales:Optional[Any]=None
    manualCardsales:Optional[Any]=None
    manualDeliverypartnersales:Optional[Any]=None
    manualOthersales:Optional[Any]=None