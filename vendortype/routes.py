from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import VendorType, VendorTypePost
from .utils import get_vendortype_collection
import pytz

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_vendortype_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "vendortypeId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_vendortype_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "vendortypeId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"VT{counter_value:03d}"


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
@router.post("/", response_model=str)
async def create_vendortype(vendortype: VendorTypePost):
    # Check if the collection is empty
    if get_vendortype_collection().count_documents({}) == 0:
        reset_counter()
    
    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_vendortype_data = vendortype.dict()
    new_vendortype_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_vendortype_collection().insert_one(new_vendortype_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[VendorType])
async def get_all_vendortype():
    vendortypes = list(get_vendortype_collection().find())
    formatted_vendortype = []
    for vendortype in vendortypes:
        vendortype["vendortypeId"] = str(vendortype["_id"])
        formatted_vendortype.append(VendorType(**vendortype))
    return formatted_vendortype

@router.get("/{vendortype_id}", response_model=VendorType)
async def get_vendortype_by_id(vendortype_id: str):
    vendortype = get_vendortype_collection().find_one({"_id": ObjectId(vendortype_id)})
    if vendortype:
        vendortype["vendortypeId"] = str(vendortype["_id"])
        return VendorType(**vendortype)
    else:
        raise HTTPException(status_code=404, detail="vendortype not found")

@router.put("/{vendortype_id}")
async def update_vendortype(vendortype_id: str, vendortype: VendorTypePost):
    updated_vendortype = vendortype.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_vendortype_collection().update_one({"_id": ObjectId(vendortype_id)}, {"$set": updated_vendortype})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="vendortype not found")
    return {"message": "vendortype updated successfully"}

@router.patch("/{vendortype_id}")
async def patch_vendortype(vendortype_id: str, vendortype_patch: VendorTypePost):
    existing_vendortype = get_vendortype_collection().find_one({"_id": ObjectId(vendortype_id)})
    if not existing_vendortype:
        raise HTTPException(status_code=404, detail="vendortype not found")

    updated_fields = {key: value for key, value in vendortype_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_vendortype_collection().update_one({"_id": ObjectId(vendortype_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update vendortype")

    updated_vendortype = get_vendortype_collection().find_one({"_id": ObjectId(vendortype_id)})
    updated_vendortype["_id"] = str(updated_vendortype["_id"])
    return updated_vendortype

@router.delete("/{vendortype_id}")
async def delete_vendortype(vendortype_id: str):
    result = get_vendortype_collection().delete_one({"_id": ObjectId(vendortype_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="vendortype not found")
    
    return {"message": "vendortype deleted successfully"}
