from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from bson import ObjectId
from .models import WareHouse, WareHousePost
from .utils import get_wareHouse_collection

router = APIRouter()


# Create a new warehouse
@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_warehouse(warehouse: WareHousePost):
    new_warehouse = warehouse.dict()
    result = get_wareHouse_collection().insert_one(new_warehouse)
    return str(result.inserted_id)


# Get all warehouses
@router.get("/", response_model=List[WareHouse])
async def get_all_warehouses():
    warehouses = list(get_wareHouse_collection().find())
    for warehouse in warehouses:
        warehouse["wareHouseId"] = str(warehouse.pop("_id"))
    return warehouses


# Get a single warehouse by ID
@router.get("/{warehouse_id}", response_model=WareHouse)
async def get_warehouse_by_id(warehouse_id: str):
    try:
        warehouse = get_wareHouse_collection().find_one({"_id": ObjectId(warehouse_id)})
        if warehouse:
            warehouse["wareHouseId"] = str(warehouse.pop("_id"))
            return warehouse
        else:
            raise HTTPException(status_code=404, detail="Warehouse not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid warehouse ID")


# Update an entire warehouse
@router.put("/{warehouse_id}")
async def update_warehouse(warehouse_id: str, warehouse_update: WareHousePost):
    updated_data = warehouse_update.dict(exclude_unset=True)
    result = get_wareHouse_collection().update_one(
        {"_id": ObjectId(warehouse_id)}, {"$set": updated_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"message": "Warehouse updated successfully"}


# Partially update a warehouse
@router.patch("/{warehouse_id}")
async def patch_warehouse(warehouse_id: str, warehouse_patch: WareHousePost):
    existing_warehouse = get_wareHouse_collection().find_one({"_id": ObjectId(warehouse_id)})
    if not existing_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    updated_fields = {
        key: value
        for key, value in warehouse_patch.dict(exclude_unset=True).items()
        if value is not None
    }

    result = get_wareHouse_collection().update_one(
        {"_id": ObjectId(warehouse_id)}, {"$set": updated_fields}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update warehouse")

    updated_warehouse = get_wareHouse_collection().find_one({"_id": ObjectId(warehouse_id)})
    updated_warehouse["wareHouseId"] = str(updated_warehouse["_id"])
    return updated_warehouse


# Delete a warehouse
@router.delete("/{warehouse_id}")
async def delete_warehouse(warehouse_id: str):
    result = get_wareHouse_collection().delete_one({"_id": ObjectId(warehouse_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"message": "Warehouse deleted successfully"}
