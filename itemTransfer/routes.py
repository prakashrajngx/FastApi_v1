from typing import List
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from .models import ItemType, ItemTypePost
from .utils import get_itemtransfer_collection




router = APIRouter()





@router.post("/", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_itemtransfer(itemtransfer: ItemTypePost):
    # Prepare data for insertion
    new_itemtransfer_data = itemtransfer.model_dump()

    # Insert into MongoDB
    result = get_itemtransfer_collection().insert_one(new_itemtransfer_data)
    return str(result.inserted_id)


@router.get("/", response_model=List[ItemType])
async def get_all_itemtransfer():
    itemtransfers = list(get_itemtransfer_collection().find())
    formatted_itemtransfer = []
    for itemtransfer in itemtransfers:
        itemtransfer["itemtransferId"] = str(itemtransfer["_id"])
        formatted_itemtransfer.append(ItemType(**itemtransfer))
    return formatted_itemtransfer

@router.get("/{itemtransfer_id}", response_model=ItemType)
async def get_itemtransfer_by_id(itemtransfer_id: str):
    itemtransfer = get_itemtransfer_collection().find_one({"_id": ObjectId(itemtransfer_id)})
    if itemtransfer:
        itemtransfer["itemtransferId"] = str(itemtransfer["_id"])
        return ItemType(**itemtransfer)
    else:
        raise HTTPException(status_code=404, detail="Itemtransfer not found")


@router.patch("/{itemtransfer_id}")
async def patch_itemtransfer(itemtransfer_id: str, itemtransfer_patch: ItemTypePost):
    existing_itemtransfer = get_itemtransfer_collection().find_one({"_id": ObjectId(itemtransfer_id)})
    if not existing_itemtransfer:
        raise HTTPException(status_code=404, detail="Itemtransfer not found")

    updated_fields = {key: value for key, value in itemtransfer_patch.model_dump(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_itemtransfer_collection().update_one({"_id": ObjectId(itemtransfer_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Itemtransfer")

    updated_itemtransfer = get_itemtransfer_collection().find_one({"_id": ObjectId(itemtransfer_id)})
    updated_itemtransfer["_id"] = str(updated_itemtransfer["_id"])
    return updated_itemtransfer

@router.delete("/{itemtransfer_id}")
async def delete_itemtransfer(itemtransfer_id: str):
    result = get_itemtransfer_collection().delete_one({"_id": ObjectId(itemtransfer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Itemtransfer not found")
    return {"message": "Itemtransfer deleted successfully"}
