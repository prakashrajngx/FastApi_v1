
from datetime import datetime
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status

from BranchDisplay.models import Employee, EmployeeGet
from BranchDisplay.utils import get_branch_report


router = APIRouter()

@router.get("/",response_model=List[EmployeeGet])
async def get_all():
    employees=list(get_branch_report().find())
    Store=[]
    for employee in employees:
        employee["id"]= str(employee["_id"])
        Store.append(EmployeeGet(**employee))
    return Store    

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_branch(branch_data:Employee):
    try:
        new_branch= branch_data.dict()
        result = get_branch_report().insert_one(new_branch)
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

  
@router.patch("/{branch_id}")
async def patch_mob(branch_id: str, branch_patch: Employee):
    try:
        existing_data = get_branch_report().find_one({"_id": ObjectId(branch_id)})
        if not existing_data:
            raise HTTPException(status_code=404, detail=" not found")

        updated_fields = {key: value for key, value in branch_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_branch_report().update_one({"_id": ObjectId(branch_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_branch = get_branch_report().find_one({"_id": ObjectId(branch_id)})
        updated_branch["_id"] = str(updated_branch["_id"])
        return updated_branch
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")      

@router.delete("/{photo_id}")
async def delete_photo(photo_id: str):
    result = get_branch_report().delete_one({"_id": ObjectId(photo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}