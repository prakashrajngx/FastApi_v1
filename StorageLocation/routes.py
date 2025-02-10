from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import StorageLocation, StorageLocationPost
from .utils import get_storagelocation_collection

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_storagelocation_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "storageLocationId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_storagelocation_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "storageLocationId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"SL{counter_value:03d}"

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
async def create_storagelocation(storagelocation: StorageLocationPost):
    # Check if the collection is empty
    if get_storagelocation_collection().count_documents({}) == 0:
        reset_counter()
    
    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_storagelocation_data = storagelocation.dict()
    new_storagelocation_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_storagelocation_collection().insert_one(new_storagelocation_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[StorageLocation])
async def get_all_storagelocation():
    storagelocations = list(get_storagelocation_collection().find())
    formated_storagelocation = []
    for storagelocation in storagelocations:
        storagelocation["storageLocationId"] = str(storagelocation["_id"])
        formated_storagelocation.append(StorageLocation(**storagelocation))
    return formated_storagelocation

@router.get("/{storageLocation_id}", response_model=StorageLocation)
async def get_storagelocation_by_id(storageLocation_id: str):
    storagelocation = get_storagelocation_collection().find_one({"_id": ObjectId(storageLocation_id)})
    if storagelocation:
        storagelocation["storageLocationId"] = str(storagelocation["_id"])
        return StorageLocation(**storagelocation)
    else:
        raise HTTPException(status_code=404, detail="StorageLocation not found")

@router.put("/{storageLocation_id}")
async def update_storagelocation(storageLocation_id: str, storagelocation: StorageLocationPost):
    updated_storagelocation = storagelocation.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_storagelocation_collection().update_one({"_id": ObjectId(storageLocation_id)}, {"$set": updated_storagelocation})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="StorageLocation not found")
    return {"message": "StorageLocation updated successfully"}

@router.patch("/{storageLocation_id}")
async def patch_storagelocation(storageLocation_id: str, storagelocation_patch: StorageLocationPost):
    existing_storagelocation = get_storagelocation_collection().find_one({"_id": ObjectId(storageLocation_id)})
    if not existing_storagelocation:
        raise HTTPException(status_code=404, detail="StorageLocation not found")

    updated_fields = {key: value for key, value in storagelocation_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_storagelocation_collection().update_one({"_id": ObjectId(storageLocation_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update StorageLocation")

    updated_storagelocation = get_storagelocation_collection().find_one({"_id": ObjectId(storageLocation_id)})
    updated_storagelocation["_id"] = str(updated_storagelocation["_id"])
    return updated_storagelocation

@router.delete("/{storageLocation_id}")
async def delete_storagelocation(storageLocation_id: str):
    result = get_storagelocation_collection().delete_one({"_id": ObjectId(storageLocation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="storagelocation not found")
    
    return {"message": "storagelocation deleted successfully"}
