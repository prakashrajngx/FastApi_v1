# routes.py

from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from pymongo.collection import Collection
from .models import CompanyStatus, CompanyStatusPost
from .utils import get_company_status_collection, convert_to_string_or_empty

router = APIRouter()

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_company_status(company_status: CompanyStatusPost):
    new_company_status = company_status.dict(exclude_unset=True)
    collection: Collection = get_company_status_collection()
    result = collection.insert_one(new_company_status)
    return str(result.inserted_id)

@router.get("/", response_model=List[CompanyStatus])
async def get_all_company_statuses():
    collection: Collection = get_company_status_collection()
    company_statuses = list(collection.find())
    formatted_company_statuses = []
    for status in company_statuses:
        status["_id"] = str(status["_id"])
        status["companyStatusId"] = status["_id"]
        formatted_company_statuses.append(CompanyStatus(**convert_to_string_or_empty(status)))
    return formatted_company_statuses

@router.get("/{companyStatusId}", response_model=CompanyStatus)
async def get_company_status_by_id(companyStatusId: str):
    if not ObjectId.is_valid(companyStatusId):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    collection: Collection = get_company_status_collection()
    company_status = collection.find_one({"_id": ObjectId(companyStatusId)})
    
    if company_status:
        company_status["_id"] = str(company_status["_id"])
        company_status["companyStatusId"] = company_status["_id"]
        return CompanyStatus(**convert_to_string_or_empty(company_status))
    else:
        raise HTTPException(status_code=404, detail="Company status not found")

@router.patch("/{companyStatusId}", response_model=CompanyStatus)
async def update_company_status(companyStatusId: str, company_status: CompanyStatusPost):
    if not ObjectId.is_valid(companyStatusId):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    updated_fields = company_status.dict(exclude_unset=True)
    collection: Collection = get_company_status_collection()
    result = collection.update_one({"_id": ObjectId(companyStatusId)}, {"$set": updated_fields})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Company status not found")
    
    return await get_company_status_by_id(companyStatusId)

@router.delete("/{companyStatusId}")
async def deactivate_company_status(companyStatusId: str):
    if not ObjectId.is_valid(companyStatusId):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    collection: Collection = get_company_status_collection()
    result = collection.update_one({"_id": ObjectId(companyStatusId)}, {"$set": {"status": "0"}})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Company status not found")
    
    return {"message": "Company status deactivated successfully"}
