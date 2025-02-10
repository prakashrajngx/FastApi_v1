from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from .utils import get_company_collection
from .models import CompanyDetails, CompanyDetailsPost

router = APIRouter()

@router.post("/", response_model=str)
async def create_company(company: CompanyDetailsPost):
    # Prepare data for insertion
    new_company_data = company.dict()

    # Insert into MongoDB
    result = get_company_collection().insert_one(new_company_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[CompanyDetails])
async def get_all_company():
    companys = list(get_company_collection().find())
    formatted_company = []
    for company in companys:
        company["companyId"] = str(company["_id"])
        formatted_company.append(CompanyDetails(**company))
    return formatted_company

@router.get("/{company_id}", response_model=CompanyDetails)
async def get_company_by_id(company_id: str):
    company = get_company_collection().find_one({"_id": ObjectId(company_id)})
    if company:
        company["companyId"] = str(company["_id"])
        return CompanyDetails(**company)
    else:
        raise HTTPException(status_code=404, detail="company not found")

@router.put("/{company_id}")
async def update_company(company_id: str, company:CompanyDetailsPost):
    updated_company= company.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_company_collection().update_one({"_id": ObjectId(company_id)}, {"$set": updated_company})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="company not found")
    return {"message": "company updated successfully"}

@router.patch("/{company_id}")
async def patch_company(company_id: str, company_patch: CompanyDetailsPost):
    existing_company = get_company_collection().find_one({"_id": ObjectId(company_id)})
    if not existing_company:
        raise HTTPException(status_code=404, detail="company not found")

    updated_fields = {key: value for key, value in company_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_company_collection().update_one({"_id": ObjectId(company_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update company")

    updated_company = get_company_collection().find_one({"_id": ObjectId(company_id)})
    updated_company["_id"] = str(updated_company["_id"])
    return updated_company

@router.delete("/{company_id}")
async def delete_company(company_id: str):
    result = get_company_collection().delete_one({"_id": ObjectId(company_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="company not found")
    return {"message": "company deleted successfully"}