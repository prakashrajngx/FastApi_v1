from datetime import datetime
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status

from empphoto.models import Employee, EmployeeGet
from empphoto.utils import get_emp_details
    

router =APIRouter()

@router.get("/", response_model=List[EmployeeGet])
async def get_all_employee():
    employees = list(get_emp_details().find())
    StoreEmployee = []
    for employee in employees:
        employee["id"] = str(employee["_id"])
        StoreEmployee.append(EmployeeGet(**employee))
    return StoreEmployee

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_emp(emp_data: Employee):
    try:
        new_emp = emp_data.dict()
        
        result = get_emp_details().insert_one(new_emp)
        return str(result.inserted_id)
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.patch("/{emp_id}")
async def patch_employee(emp_id: str, lunch_patch: Employee):
    try:
        existing_vendor = get_emp_details().find_one({"_id": ObjectId(emp_id)})
        if not existing_vendor:
            raise HTTPException(status_code=404, detail="Lunch not found")
        updated_fields = {key: value for key, value in lunch_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_emp_details().update_one({"_id": ObjectId(emp_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_employee = get_emp_details().find_one({"_id": ObjectId(emp_id)})
        updated_employee["_id"] = str(updated_employee["_id"])
        return updated_employee
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")    

@router.delete("/{photo_id}")
async def delete_photo(photo_id: str):
    result = get_emp_details().delete_one({"_id": ObjectId(photo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}