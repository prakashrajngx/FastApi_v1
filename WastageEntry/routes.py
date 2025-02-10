from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import WastageEntry, WastageEntryPost
from .utils import get_wastage_entry_collection

router = APIRouter()

@router.post("/", response_model=str)
async def create_wastage_entry(wastage_entry: WastageEntryPost):
    # Prepare data for insertion
    new_wastage_entry_data = wastage_entry.dict()

    # Insert into MongoDB
    result = get_wastage_entry_collection().insert_one(new_wastage_entry_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[WastageEntry])
async def get_all_wastage_entries():
    wastage_entries = list(get_wastage_entry_collection().find())
    formatted_wastage_entries = []
    for entry in wastage_entries:
        entry["wastageId"] = str(entry["_id"])
        formatted_wastage_entries.append(WastageEntry(**entry))
    return formatted_wastage_entries

@router.get("/{wastage_entry_id}", response_model=WastageEntry)
async def get_wastage_entry_by_id(wastage_entry_id: str):
    wastage_entry = get_wastage_entry_collection().find_one({"_id": ObjectId(wastage_entry_id)})
    if wastage_entry:
        wastage_entry["wastageId"] = str(wastage_entry["_id"])
        return WastageEntry(**wastage_entry)
    else:
        raise HTTPException(status_code=404, detail="Wastage entry not found")

@router.put("/{wastage_entry_id}")
async def update_wastage_entry(wastage_entry_id: str, wastage_entry: WastageEntryPost):
    updated_wastage_entry = wastage_entry.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_wastage_entry_collection().update_one({"_id": ObjectId(wastage_entry_id)}, {"$set": updated_wastage_entry})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Wastage entry not found")
    return {"message": "Wastage entry updated successfully"}

@router.patch("/{wastage_entry_id}")
async def patch_wastage_entry(wastage_entry_id: str, wastage_entry_patch: WastageEntryPost):
    existing_wastage_entry = get_wastage_entry_collection().find_one({"_id": ObjectId(wastage_entry_id)})
    if not existing_wastage_entry:
        raise HTTPException(status_code=404, detail="Wastage entry not found")

    updated_fields = {key: value for key, value in wastage_entry_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_wastage_entry_collection().update_one({"_id": ObjectId(wastage_entry_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update wastage entry")

    updated_wastage_entry = get_wastage_entry_collection().find_one({"_id": ObjectId(wastage_entry_id)})
    updated_wastage_entry["_id"] = str(updated_wastage_entry["_id"])
    return updated_wastage_entry

@router.delete("/{wastage_entry_id}")
async def delete_wastage_entry(wastage_entry_id: str):
    result = get_wastage_entry_collection().delete_one({"_id": ObjectId(wastage_entry_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Wastage entry not found")
    return {"message": "Wastage entry deleted successfully"}
