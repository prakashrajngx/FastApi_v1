

import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status
from LunchCount.utils import  get_lunch_count
from LunchCount.models import Lunch, LunchGet

router = APIRouter()
@router.get("/", response_model=List[LunchGet])
async def get_all_vendor():
    lunches = list(get_lunch_count().find())
    Lunchstore = []
    for Lunch in lunches:
        Lunch["id"] = str(Lunch["_id"])
        Lunchstore.append(LunchGet(**Lunch))
    return Lunchstore

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_lunch(lunch_data: LunchGet):
    try:
        new_lunch = lunch_data.dict()
        
        result = get_lunch_count().insert_one(new_lunch)
        return str(result.inserted_id)
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.patch("/{lunch_id}",response_model=LunchGet)
async def patch_lunch(lunch_id: str, lunch_patch: Lunch):
    try:
        existing_vendor = get_lunch_count().find_one({"_id": ObjectId(lunch_id)})
        if not existing_vendor:
            raise HTTPException(status_code=404, detail="Lunch not found")

        updated_fields = {key: value for key, value in lunch_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_lunch_count().update_one({"_id": ObjectId(lunch_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_vendor = get_lunch_count().find_one({"_id": ObjectId(lunch_id)})
        updated_vendor["_id"] = str(updated_vendor["_id"])
        return updated_vendor
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")    

