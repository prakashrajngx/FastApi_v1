# app/dailylist/Ebreading/routes.py
from fastapi import APIRouter, HTTPException,status 
from typing import List
from Ebreading.utils import  ebreading_collection  # Assuming this is your MongoDB collection
from Ebreading.models import BranchPost, Meter, BranchResponse
from bson import ObjectId
import logging
router = APIRouter()
@router.get("/", response_model=List[BranchResponse])
async def get_all_branches():
    documents = list(ebreading_collection().find())
    fomatted_reading =[]
    for reading_dict in documents:
        reading_dict['id'] = str(reading_dict["_id"])
        fomatted_reading.append(BranchResponse(**reading_dict))
    return fomatted_reading

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_reading(read_data:BranchPost):
    try:
        new_reading=read_data.dict()
        result =ebreading_collection().insert_one(new_reading)
        return str(result.inserted_id)
      
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@router.patch("/{branch_id}", response_model=BranchPost)
async def upd_reading(branch_id: str, read_patch: BranchPost):
    try:
        # Correctly find the existing reading
        existing_reading = ebreading_collection().find_one({"_id": ObjectId(branch_id)})  # Use branch_id here
        if not existing_reading:
            raise HTTPException(status_code=404, detail="Reading not found")

        # Create a dictionary of updated fields
        updated_fields = {key: value for key, value in read_patch.dict(exclude_unset=True).items() if value is not None}

        # Update the reading if there are updated fields
        if updated_fields:
            result = ebreading_collection().update_one({"_id": ObjectId(branch_id)}, {"$set": updated_fields})  # Use branch_id here
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update reading")

        # Retrieve the updated reading
        updated_reading = ebreading_collection().find_one({"_id": ObjectId(branch_id)})  # Use branch_id here
        if updated_reading is None:
            raise HTTPException(status_code=404, detail="Reading not found after update")

        updated_reading["_id"] = str(updated_reading["_id"])  # Convert ObjectId to string
        return updated_reading

    except Exception as e:
        logging.error(f"Error occurred while patching reading: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

