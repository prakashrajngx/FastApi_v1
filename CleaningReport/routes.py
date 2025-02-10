
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status

from CleaningReport .models import Employee,EmployeeGet
from CleaningReport.utils import get_cleaning_video


router = APIRouter()

@router.get("/",response_model=List[EmployeeGet])
async def get_all():
    employees=list(get_cleaning_video().find())
    Store=[]
    for employee in employees:
        employee["id"]= str(employee["_id"])
        Store.append(EmployeeGet(**employee))
    return Store    

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_video(video_data:Employee):
    try:
        new_video= video_data.dict()
        result = get_cleaning_video().insert_one(new_video)
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

  
@router.patch("/{video_id}")
async def patch_mob(video_id: str, branch_patch: Employee):
    try:
        existing_data = get_cleaning_video().find_one({"_id": ObjectId(video_id)})
        if not existing_data:
            raise HTTPException(status_code=404, detail=" not found")

        updated_fields = {key: value for key, value in branch_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_cleaning_video().update_one({"_id": ObjectId(video_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_video = get_cleaning_video().find_one({"_id": ObjectId(video_id)})
        updated_video["_id"] = str(updated_video["_id"])
        return updated_video
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")      

@router.delete("/{video_id}")
async def delete_photo(video_id: str):
    result = get_cleaning_video().delete_one({"_id": ObjectId(video_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}