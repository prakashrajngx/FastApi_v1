
import logging
from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException,status


from kraSheet.models import Employee, EmployeeGet
from  kraSheet.utils import get_clean_report



router = APIRouter()

@router.get("/",response_model=List[EmployeeGet])
async def get_all():
    employees=list(get_clean_report().find())
    Store=[]
    for employee in employees:
        employee["id"]= str(employee["_id"])
        Store.append(EmployeeGet(**employee))
    return Store    

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_report(report:Employee):
    try:
        new_report= report.dict()
        result = get_clean_report().insert_one(new_report)
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

  
@router.patch("/{clean_id}")
async def patch_clean(clean_id: str, clean_patch: Employee):
    try:
        existing_data = get_clean_report().find_one({"_id": ObjectId(clean_id)})
        if not existing_data:
            raise HTTPException(status_code=404, detail=" not found")

        updated_fields = {key: value for key, value in clean_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            result = get_clean_report().update_one({"_id": ObjectId(clean_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_vendor = get_clean_report().find_one({"_id": ObjectId(clean_id)})
        updated_vendor["_id"] = str(updated_vendor["_id"])
        return updated_vendor
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")      

@router.delete("/{clean_id}")
async def delete_vendor(clean_id: str):
    result = get_clean_report().delete_one({"_id": ObjectId(clean_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}