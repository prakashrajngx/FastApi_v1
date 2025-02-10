
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status

from mobilesubmission.models import Mobile, MobileGet
from mobilesubmission.utils import get_mobile_details


router = APIRouter()

@router.get("/",response_model=List[MobileGet])
async def get_all():
    employees=list(get_mobile_details().find())
    Store=[]
    for employee in employees:
        employee["id"]= str(employee["_id"])
        Store.append(MobileGet(**employee))
    return Store    

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_mobile(mob_data:Mobile):
    try:
        new_mobile= mob_data.dict()
        result = get_mobile_details().insert_one(new_mobile)
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

  
@router.patch("/{mob_id}")
async def patch_mob(mob_id: str, mob_patch: Mobile):
    try:
        existing_data = get_mobile_details().find_one({"_id": ObjectId(mob_id)})
        if not existing_data:
            raise HTTPException(status_code=404, detail=" not found")

        updated_fields = {key: value for key, value in mob_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_mobile_details().update_one({"_id": ObjectId(mob_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_vendor = get_mobile_details().find_one({"_id": ObjectId(mob_id)})
        updated_vendor["_id"] = str(updated_vendor["_id"])
        return updated_vendor
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")      

@router.delete("/{photo_id}")
async def delete_photo(photo_id: str):
    result = get_mobile_details().delete_one({"_id": ObjectId(photo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}