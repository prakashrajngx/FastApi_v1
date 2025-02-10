from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import PurchaseTax, PurchaseTaxPost
from .utils import get_purchasetax_collection

router = APIRouter()

# Function to get the current date and time with timezone as a datetime object
def get_current_date_and_time(timezone: str = "Asia/Kolkata") -> datetime:
    try:
        # Set the specified timezone
        specified_timezone = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    
    # Get the current time in the specified timezone and make it timezone-aware
    now = datetime.now(specified_timezone)
    
    return {
        "datetime": now  # Return the ISO 8601 formatted datetime string
    }
def get_next_counter_value():
    counter_collection = get_purchasetax_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchasetaxId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_purchasetax_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchasetaxId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PT{counter_value:03d}"

@router.post("/", response_model=str)
async def create_purchasetax(purchasetax: PurchaseTaxPost):
    # Check if the collection is empty
    if get_purchasetax_collection().count_documents({}) == 0:
        reset_counter()
    
    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_purchasetax_data = purchasetax.dict()
    new_purchasetax_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_purchasetax_collection().insert_one(new_purchasetax_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[PurchaseTax])
async def get_all_purchasetax():
    purchasetaxs = list(get_purchasetax_collection().find())
    formatted_purchasetax = []
    for purchasetax in purchasetaxs:
        purchasetax["purchasetaxId"] = str(purchasetax["_id"])
        formatted_purchasetax.append(PurchaseTax(**purchasetax))
    return formatted_purchasetax

@router.get("/{purchasetax_id}", response_model=PurchaseTax)
async def get_purchasetax_by_id(purchasetax_id: str):
    purchasetax = get_purchasetax_collection().find_one({"_id": ObjectId(purchasetax_id)})
    if purchasetax:
        purchasetax["purchasetaxId"] = str(purchasetax["_id"])
        return PurchaseTax(**purchasetax)
    else:
        raise HTTPException(status_code=404, detail="PurchaseTax not found")

@router.put("/{purchasetax_id}")
async def update_PurchaseTax(purchasetax_id: str, purchasetax: PurchaseTaxPost):
    updated_purchasetax = purchasetax.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_purchasetax_collection().update_one({"_id": ObjectId(purchasetax_id)}, {"$set": updated_purchasetax})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseTax not found")
    return {"message": "PurchaseTax updated successfully"}

@router.patch("/{purchasetax_id}")
async def patch_purchasetax(purchasetax_id: str, purchasetax_patch: PurchaseTaxPost):
    existing_purchasetax = get_purchasetax_collection().find_one({"_id": ObjectId(purchasetax_id)})
    if not existing_purchasetax:
        raise HTTPException(status_code=404, detail="PurchaseTax not found")

    updated_fields = {key: value for key, value in purchasetax_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_purchasetax_collection().update_one({"_id": ObjectId(purchasetax_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update PurchaseTax")

    updated_purchasetax = get_purchasetax_collection().find_one({"_id": ObjectId(purchasetax_id)})
    updated_purchasetax["_id"] = str(updated_purchasetax["_id"])
    return updated_purchasetax

@router.delete("/{purchasetax_id}")
async def delete_purchasetax(purchasetax_id: str):
    result = get_purchasetax_collection().delete_one({"_id": ObjectId(purchasetax_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseTax not found")
    
    return {"message": "PurchaseTax deleted successfully"}
