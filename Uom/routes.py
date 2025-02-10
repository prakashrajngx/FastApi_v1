from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import uom, uomPost
from .utils import get_uom_collection, convert_to_string_or_none

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_uom_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "uomId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_uom_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "uomId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IU{counter_value:03d}"

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_uom(uom: uomPost):
    # Check if the collection is empty
    if get_uom_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_uom_data = uom.dict()
    new_uom_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_uom_collection().insert_one(new_uom_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[uom])
async def get_all_uom():
    try:
        itemuom = list(get_uom_collection().find())
        formatted_uom = []
        for uoms in itemuom:
            for key, value in uoms.items():
                uoms[key] = convert_to_string_or_none(value)
            uoms["uomId"] = str(uoms["_id"])
            formatted_uom.append(uom(**uoms))
        return formatted_uom
    except Exception as e:
        print(f"Error fetching UOMs: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{uom_id}", response_model=uom)
async def get_uom_by_id(uom_id: str):
    try:
        uom_data = get_uom_collection().find_one({"_id": ObjectId(uom_id)})
        if uom_data:
            uom_data["uomId"] = str(uom_data["_id"])
            return uom(**uom_data)
        else:
            raise HTTPException(status_code=404, detail="uom not found")
    except Exception as e:
        print(f"Error fetching UOM by ID: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{uom_id}")
async def update_uom(uom_id: str, uom: uomPost):
    updated_uom = uom.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_uom_collection().update_one({"_id": ObjectId(uom_id)}, {"$set": updated_uom})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="uom not found")
    return {"message": "uom updated successfully"}

@router.patch("/{uom_id}")
async def patch_uom(uom_id: str, uom_patch: uomPost):
    existing_uom = get_uom_collection().find_one({"_id": ObjectId(uom_id)})
    if not existing_uom:
        raise HTTPException(status_code=404, detail="uom not found")

    updated_fields = {key: value for key, value in uom_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_uom_collection().update_one({"_id": ObjectId(uom_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update uom")

    updated_uom = get_uom_collection().find_one({"_id": ObjectId(uom_id)})
    updated_uom["_id"] = str(updated_uom["_id"])
    return updated_uom

@router.delete("/{uom_id}")
async def delete_uom(uom_id: str):
    result = get_uom_collection().delete_one({"_id": ObjectId(uom_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="uom not found")
    return {"message": "uom deleted successfully"}
