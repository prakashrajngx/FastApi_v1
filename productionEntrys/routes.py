from typing import List,Optional
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from .models import ProductionEntry, ProductionEntryPost
from .utils import get_productionEntry_collection
from datetime import datetime, timedelta



router = APIRouter()

@router.post("/", response_model=str)
async def create_production_entry(production_entry: ProductionEntryPost):
    # Prepare data for insertion
    new_production_entry_data = production_entry.dict()

    # Insert into MongoDB
    result = get_productionEntry_collection().insert_one(new_production_entry_data)
    return str(result.inserted_id)


@router.get("/", response_model=List[ProductionEntry])
async def get_all_production_entries(date: Optional[str] = Query(None)):
    """
    Fetch all production entries, optionally filtering by a specific date.

    :param date: A string in DD-MM-YYYY format for filtering entries by date.
    :return: A list of ProductionEntry objects.
    """
    # Prepare the MongoDB query
    query = {}
    if date:
        try:
            # Parse the provided date and filter for the entire day
            date_obj = datetime.strptime(date, "%d-%m-%Y")
            start_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            query["date"] = {"$gte": start_date.isoformat(), "$lt": (end_date + timedelta(seconds=1)).isoformat()}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY.")

    # Fetch data from the collection with the query
    production_entries = list(get_productionEntry_collection().find(query))

    # Format and serialize the entries
    formatted_production_entries = []
    for entry in production_entries:
        entry["productionEntryId"] = str(entry["_id"])  # Convert ObjectId to string
        formatted_production_entries.append(ProductionEntry(**entry))

    return formatted_production_entries

@router.get("/{production_entry_id}", response_model=ProductionEntry)
async def get_production_entry_by_id(production_entry_id: str):
    production_entry = get_productionEntry_collection().find_one({"_id": ObjectId(production_entry_id)})
    if production_entry:
        production_entry["productionEntryId"] = str(production_entry["_id"])
        return ProductionEntry(**production_entry)
    else:
        raise HTTPException(status_code=404, detail="ProductionEntry not found")

@router.put("/{production_entry_id}")
async def update_production_entry(production_entry_id: str, production_entry: ProductionEntryPost):
    updated_production_entry = production_entry.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_productionEntry_collection().update_one({"_id": ObjectId(production_entry_id)}, {"$set": updated_production_entry})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="ProductionEntry not found")
    return {"message": "ProductionEntry updated successfully"}

@router.patch("/{production_entry_id}")
async def patch_production_entry(production_entry_id: str, production_entry_patch: ProductionEntryPost):
    existing_production_entry = get_productionEntry_collection().find_one({"_id": ObjectId(production_entry_id)})
    if not existing_production_entry:
        raise HTTPException(status_code=404, detail="ProductionEntry not found")

    updated_fields = {key: value for key, value in production_entry_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_productionEntry_collection().update_one({"_id": ObjectId(production_entry_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update ProductionEntry")

    updated_production_entry = get_productionEntry_collection().find_one({"_id": ObjectId(production_entry_id)})
    updated_production_entry["_id"] = str(updated_production_entry["_id"])
    return updated_production_entry

@router.delete("/{production_entry_id}")
async def delete_production_entry(production_entry_id: str):
    result = get_productionEntry_collection().delete_one({"_id": ObjectId(production_entry_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="ProductionEntry not found")
    return {"message": "ProductionEntry deleted successfully"}
