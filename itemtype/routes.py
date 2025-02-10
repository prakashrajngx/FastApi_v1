from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import ItemType, ItemTypePost
from .utils import get_itemtype_collection

router = APIRouter()
item_group_counter = 0

def get_next_counter_value():
    counter_collection = get_itemtype_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "itemtypeId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_itemtype_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "itemtypeId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IT{counter_value:03d}"


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
async def create_itemtype(itemtype: ItemTypePost):
    # Check if the collection is empty
    if get_itemtype_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_itemtype_data = itemtype.dict()
    new_itemtype_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_itemtype_collection().insert_one(new_itemtype_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[ItemType])
async def get_all_itemtype():
    itemtypes = list(get_itemtype_collection().find())
    formatted_itemtype = []
    for itemtype in itemtypes:
        itemtype["itemtypeId"] = str(itemtype["_id"])
        formatted_itemtype.append(ItemType(**itemtype))
    return formatted_itemtype

@router.get("/{itemtype_id}", response_model=ItemType)
async def get_itemtype_by_id(itemtype_id: str):
    itemtype = get_itemtype_collection().find_one({"_id": ObjectId(itemtype_id)})
    if itemtype:
        itemtype["itemtypeId"] = str(itemtype["_id"])
        return ItemType(**itemtype)
    else:
        raise HTTPException(status_code=404, detail="Itemtype not found")

@router.put("/{itemtype_id}")
async def update_itemtype(itemtype_id: str, itemtype: ItemTypePost):
    updated_itemtype = itemtype.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_itemtype_collection().update_one({"_id": ObjectId(itemtype_id)}, {"$set": updated_itemtype})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Itemtype not found")
    return {"message": "Itemtype updated successfully"}

@router.patch("/{itemtype_id}")
async def patch_itemtype(itemtype_id: str, itemtype_patch: ItemTypePost):
    existing_itemtype = get_itemtype_collection().find_one({"_id": ObjectId(itemtype_id)})
    if not existing_itemtype:
        raise HTTPException(status_code=404, detail="Itemtype not found")

    updated_fields = {key: value for key, value in itemtype_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_itemtype_collection().update_one({"_id": ObjectId(itemtype_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Itemtype")

    updated_itemtype = get_itemtype_collection().find_one({"_id": ObjectId(itemtype_id)})
    updated_itemtype["_id"] = str(updated_itemtype["_id"])
    return updated_itemtype

@router.delete("/{itemtype_id}")
async def delete_itemtype(itemtype_id: str):
    result = get_itemtype_collection().delete_one({"_id": ObjectId(itemtype_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Itemtype not found")
    return {"message": "Itemtype deleted successfully"}
