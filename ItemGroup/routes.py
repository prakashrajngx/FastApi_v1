from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from ItemGroup.models import ItemGroup, ItemGroupPost
from ItemGroup.utils import get_itemgroup_collection

router = APIRouter()
item_group_counter = 0

def get_next_counter_value():
    counter_collection = get_itemgroup_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "itemgroupId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_itemgroup_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "itemgroupId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IG{counter_value:03d}"


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
async def create_itemgroup(itemgroup: ItemGroupPost):
    # Check if the collection is empty
    if get_itemgroup_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_itemgroup_data = itemgroup.dict()
    new_itemgroup_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_itemgroup_collection().insert_one(new_itemgroup_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[ItemGroup])
async def get_all_itemgroup():
    itemgroups = list(get_itemgroup_collection().find())
    formatted_itemgroup = []
    for itemgroup in itemgroups:
        itemgroup["itemgroupId"] = str(itemgroup["_id"])
        formatted_itemgroup.append(ItemGroup(**itemgroup))
    return formatted_itemgroup

@router.get("/{itemgroup_id}", response_model=ItemGroup)
async def get_itemgroup_by_id(itemgroup_id: str):
    itemgroup = get_itemgroup_collection().find_one({"_id": ObjectId(itemgroup_id)})
    if itemgroup:
        itemgroup["itemgroupId"] = str(itemgroup["_id"])
        return ItemGroup(**itemgroup)
    else:
        raise HTTPException(status_code=404, detail="Itemgroup not found")

@router.put("/{itemgroup_id}")
async def update_itemgroup(itemgroup_id: str, itemgroup: ItemGroupPost):
    updated_itemgroup = itemgroup.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_itemgroup_collection().update_one({"_id": ObjectId(itemgroup_id)}, {"$set": updated_itemgroup})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Itemgroup not found")
    return {"message": "Itemgroup updated successfully"}

@router.patch("/{itemgroup_id}")
async def patch_itemgroup(itemgroup_id: str, itemgroup_patch: ItemGroupPost):
    existing_itemgroup = get_itemgroup_collection().find_one({"_id": ObjectId(itemgroup_id)})
    if not existing_itemgroup:
        raise HTTPException(status_code=404, detail="Itemgroup not found")

    updated_fields = {key: value for key, value in itemgroup_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_itemgroup_collection().update_one({"_id": ObjectId(itemgroup_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Itemgroup")

    updated_itemgroup = get_itemgroup_collection().find_one({"_id": ObjectId(itemgroup_id)})
    updated_itemgroup["_id"] = str(updated_itemgroup["_id"])
    return updated_itemgroup

@router.delete("/{itemgroup_id}")
async def delete_itemgroup(itemgroup_id: str):
    result = get_itemgroup_collection().delete_one({"_id": ObjectId(itemgroup_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Itemgroup not found")
    return {"message": "Itemgroup deleted successfully"}
