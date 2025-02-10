from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import itemSubcategory, itemSubcategoryPost
from .utils import get_itemsubcategory_collection, convert_to_string_or_none

router = APIRouter()
item_category_counter = 0

def get_next_counter_value():
    counter_collection = get_itemsubcategory_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "subCategoryId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_itemsubcategory_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "subCategoryId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IS{counter_value:03d}"

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_itemsubcategory(itemsubcategory: itemSubcategoryPost):
    # Check if the collection is empty
    if get_itemsubcategory_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_itemsubcategory_data = itemsubcategory.dict()
    new_itemsubcategory_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_itemsubcategory_collection().insert_one(new_itemsubcategory_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[itemSubcategory])
async def get_all_itemsubcategory():
    itemsubcategories = list(get_itemsubcategory_collection().find())
    formatted_itemsubcategory = []
    for itemsubcategory in itemsubcategories:
        for key,value in itemsubcategory.items():
            itemsubcategory[key]=convert_to_string_or_none(value)
        itemsubcategory["subCategoryId"] = str(itemsubcategory["_id"])
        formatted_itemsubcategory.append(itemSubcategory(**itemsubcategory))
    return formatted_itemsubcategory

@router.get("/{itemsubcategory_id}", response_model=itemSubcategory)
async def get_itemsubcategory_by_id(itemsubcategory_id: str):
    itemsubcategory = get_itemsubcategory_collection().find_one({"_id": ObjectId(itemsubcategory_id)})
    if itemsubcategory:
        itemsubcategory["subCategoryId"] = str(itemsubcategory["_id"])
        return itemSubcategory(**itemsubcategory)
    else:
        raise HTTPException(status_code=404, detail="itemsubcategory not found")

@router.put("/{itemsubcategory_id}")
async def update_itemsubcategory(itemsubcategory_id: str, itemsubcategory: itemSubcategoryPost):
    updated_itemsubcategory = itemsubcategory.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_itemsubcategory_collection().update_one({"_id": ObjectId(itemsubcategory_id)}, {"$set": updated_itemsubcategory})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="itemsubcategory not found")
    return {"message": "itemsubcategory updated successfully"}

@router.patch("/{itemsubcategory_id}")
async def patch_itemsubcategory(itemsubcategory_id: str, itemsubcategory_patch: itemSubcategoryPost):
    existing_itemsubcategory = get_itemsubcategory_collection().find_one({"_id": ObjectId(itemsubcategory_id)})
    if not existing_itemsubcategory:
        raise HTTPException(status_code=404, detail="itemsubcategory not found")

    updated_fields = {key: value for key, value in itemsubcategory_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_itemsubcategory_collection().update_one({"_id": ObjectId(itemsubcategory_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update itemsubcategory")

    updated_itemsubcategory = get_itemsubcategory_collection().find_one({"_id": ObjectId(itemsubcategory_id)})
    updated_itemsubcategory["_id"] = str(updated_itemsubcategory["_id"])
    return updated_itemsubcategory

@router.delete("/{itemsubcategory_id}")
async def delete_itemsubcategory(itemsubcategory_id: str):
    result = get_itemsubcategory_collection().delete_one({"_id": ObjectId(itemsubcategory_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="itemsubcategory not found")
    return {"message": "itemsubcategory deleted successfully"}
