from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from addOn.models import addOn, addOnPost
from addOn.utils import get_addOn_collection, convert_to_string_or_none

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_addOn_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "addOnId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_addOn_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "addOnId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"AO{counter_value:03d}"

@router.post("/", response_model=str)
async def create_addOn(addOn: addOnPost):
    # Check if the collection is empty
    if get_addOn_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_addOn_data = addOn.dict()
    new_addOn_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_addOn_collection().insert_one(new_addOn_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[addOn])
async def get_all_addOn():
    try:
        itemaddOn = list(get_addOn_collection().find())
        formatted_addOn = []
        for addOns in itemaddOn:
            addOns["_id"] = str(addOns["_id"])  # Ensure _id is a string
            for key, value in addOns.items():
                addOns[key] = convert_to_string_or_none(value)
            addOns["addOnId"] = addOns["_id"]
            formatted_addOn.append(addOn(**addOns))
        return formatted_addOn
    except Exception as e:
        print(f"Error fetching addOns: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@router.get("/", response_model=List[addOn])
async def get_all_addOn():
    try:
        itemaddOn = list(get_addOn_collection().find())
        formatted_addOn = []
        for addOns in itemaddOn:
            addOns["_id"] = str(addOns["_id"])  # Convert _id to string
            # Ensure all keys are present; provide defaults if needed
            addOns["addOnItems"] = addOns.get("addOnItems", [])
            addOns["addOnId"] = addOns["_id"]
            formatted_addOn.append(addOn(**addOns))
        return formatted_addOn
    except Exception as e:
        print(f"Error fetching addOns: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{addOn_id}")
async def update_addOn(addOn_id: str, addOn: addOnPost):
    if not ObjectId.is_valid(addOn_id):
        raise HTTPException(status_code=400, detail="Invalid addOnId format")
    
    updated_addOn = addOn.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_addOn_collection().update_one({"_id": ObjectId(addOn_id)}, {"$set": updated_addOn})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="addOn not found")
    return {"message": "addOn updated successfully"}

@router.patch("/{addOn_id}")
async def patch_addOn(addOn_id: str, addOn_patch: addOnPost):
    if not ObjectId.is_valid(addOn_id):
        raise HTTPException(status_code=400, detail="Invalid addOnId format")
    
    existing_addOn = get_addOn_collection().find_one({"_id": ObjectId(addOn_id)})
    if not existing_addOn:
        raise HTTPException(status_code=404, detail="addOn not found")

    updated_fields = {key: value for key, value in addOn_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_addOn_collection().update_one({"_id": ObjectId(addOn_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update addOn")

    updated_addOn = get_addOn_collection().find_one({"_id": ObjectId(addOn_id)})
    updated_addOn["_id"] = str(updated_addOn["_id"])
    return updated_addOn

@router.delete("/{addOn_id}")
async def delete_addOn(addOn_id: str):
    if not ObjectId.is_valid(addOn_id):
        raise HTTPException(status_code=400, detail="Invalid addOnId format")
    
    result = get_addOn_collection().delete_one({"_id": ObjectId(addOn_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="addOn not found")
    return {"message": "addOn deleted successfully"}
