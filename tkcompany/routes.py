from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import Company, CompanyPost
from .utils import get_company_collection, convert_to_string_or_emptys

router = APIRouter()

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyPost):
    new_company = dict(company)
    new_company['status'] = '1'  # Default to active
    result = get_company_collection().insert_one(new_company)
    return str(result.inserted_id)

@router.get("/", response_model=List[Company])
async def get_all_companies():
    companies = list(get_company_collection().find())
    formatted_companies = []
    for company in companies:
        company["_id"] = str(company["_id"])
        company["companyId"] = company["_id"]
        formatted_companies.append(Company(**convert_to_string_or_emptys(company)))
    return formatted_companies

@router.get("/{companyId}", response_model=Company)
async def get_company_by_id(companyId: str):
    company = get_company_collection().find_one({"_id": ObjectId(companyId)})
    if company:
        company["_id"] = str(company["_id"])
        company["companyId"] = company["_id"]
        return Company(**convert_to_string_or_emptys(company))
    else:
        raise HTTPException(status_code=404, detail="Company not found")

@router.patch("/{companyId}")
async def update_company(companyId: str, company: CompanyPost):
    updated_fields = company.dict(exclude_unset=True)
    result = get_company_collection().update_one(
        {"_id": ObjectId(companyId)},
        {"$set": convert_to_string_or_emptys(updated_fields)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company updated successfully"}

@router.patch("/{companyId}/deactivate")
async def deactivate_company(companyId: str):
    result = get_company_collection().update_one(
        {"_id": ObjectId(companyId)},
        {"$set": {"status": "0"}}  # Assuming status '0' means deactivated
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deactivated successfully"}

@router.patch("/{companyId}/activate")
async def activate_company(companyId: str):
    result = get_company_collection().update_one(
        {"_id": ObjectId(companyId)},
        {"$set": {"status": "1"}}  # Assuming status '1' means activated
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company activated successfully"}

@router.delete("/{companyId}")
async def delete_company(companyId: str):
    result = get_company_collection().delete_one({"_id": ObjectId(companyId)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted successfully"}
