from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import tax, taxPost
from .utils import get_tax_collection, convert_to_string_or_none

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_tax_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "taxId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_tax_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "taxId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IT{counter_value:03d}"

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_tax(tax: taxPost):
    # Check if the collection is empty
    if get_tax_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_tax_data = tax.dict()
    new_tax_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_tax_collection().insert_one(new_tax_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[tax])
async def get_all_tax():
    try:
        itemtax = list(get_tax_collection().find())
        formatted_tax = []
        for taxs in itemtax:
            for key, value in taxs.items():
                taxs[key] = convert_to_string_or_none(value)
            taxs["taxId"] = str(taxs["_id"])
            formatted_tax.append(tax(**taxs))
        return formatted_tax
    except Exception as e:
        print(f"Error fetching taxs: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{tax_id}", response_model=tax)
async def get_tax_by_id(tax_id: str):
    try:
        tax_data = get_tax_collection().find_one({"_id": ObjectId(tax_id)})
        if tax_data:
            tax_data["taxId"] = str(tax_data["_id"])
            return tax(**tax_data)
        else:
            raise HTTPException(status_code=404, detail="tax not found")
    except Exception as e:
        print(f"Error fetching tax by ID: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{tax_id}")
async def update_tax(tax_id: str, tax: taxPost):
    updated_tax = tax.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_tax_collection().update_one({"_id": ObjectId(tax_id)}, {"$set": updated_tax})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="tax not found")
    return {"message": "tax updated successfully"}

@router.patch("/{tax_id}")
async def patch_tax(tax_id: str, tax_patch: taxPost):
    existing_tax = get_tax_collection().find_one({"_id": ObjectId(tax_id)})
    if not existing_tax:
        raise HTTPException(status_code=404, detail="tax not found")

    updated_fields = {key: value for key, value in tax_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_tax_collection().update_one({"_id": ObjectId(tax_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update tax")

    updated_tax = get_tax_collection().find_one({"_id": ObjectId(tax_id)})
    updated_tax["_id"] = str(updated_tax["_id"])
    return updated_tax

@router.delete("/{tax_id}")
async def delete_tax(tax_id: str):
    result = get_tax_collection().delete_one({"_id": ObjectId(tax_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="tax not found")
    return {"message": "tax deleted successfully"}

