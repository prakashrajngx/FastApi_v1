

from datetime import datetime
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException

from MilkReceivings.models import MilkReceiving, MilkReceivingResponse
from MilkReceivings.utils import  get_milk

router = APIRouter()

@router.post("/", response_model=MilkReceivingResponse)
async def create_milk_receiving(milk: MilkReceiving):
    milk_dict = milk.dict()
    result =  get_milk().insert_one(milk_dict)
    milk_dict['id'] = str(result.inserted_id)
    return milk_dict

# Get all milk receiving entries
@router.get("/", response_model=List[MilkReceivingResponse])
async def get_milk_receivings():
    milks= list(get_milk().find())
    milk_receivings = []
    for Milk in milks:
        Milk['id'] = str(Milk['_id'])
        milk_receivings.append(MilkReceivingResponse(**Milk))
    return milk_receivings


@router.patch("/{milk_id}")
async def patch_milk(milk_id: str, milk_patch: MilkReceiving):
    try:
        existing_vendor = get_milk().find_one({"_id": ObjectId(milk_id)})
        if not existing_vendor:
            raise HTTPException(status_code=404, detail="Entry not found")

        # Convert the patch model to a dictionary, excluding unset fields
        updated_fields = {key: value for key, value in milk_patch.dict(exclude_unset=True).items() if value is not None}

        # Only add updatedDate to the update fields
        updated_fields['updatedDate'] = datetime.now()  # Set to current time on update

        if updated_fields:
            # Do not update the date; only update other fields
            updated_fields.pop('date', None)  # Ensure date is not updated

            result = get_milk().update_one({"_id": ObjectId(milk_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_vendor = get_milk().find_one({"_id": ObjectId(milk_id)})
        updated_vendor["_id"] = str(updated_vendor["_id"])
        return updated_vendor
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{milkid}")
async def delete_vendor(milkid: str):
    result = get_milk().delete_one({"_id": ObjectId(milkid)})  
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}