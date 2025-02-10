from fastapi import APIRouter, HTTPException, Body, Path,status
from typing import List
from bson import ObjectId
from mixBox.models import MixBox, MixBoxPost
from mixBox.utils import get_mixbox_collection

router = APIRouter()
collection = get_mixbox_collection()

# Helper function to convert ObjectId to string
def convert_object_id(item):
    if isinstance(item, dict):
        if "_id" in item:
            item["_id"] = str(item["_id"])
        return {k: convert_object_id(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [convert_object_id(i) for i in item]
    return item
@router.post("/", response_model=MixBox,status_code=status.HTTP_201_CREATED)
def create_mixbox(mixbox: MixBoxPost):
    mixbox_dict = mixbox.dict()
    result = collection.insert_one(mixbox_dict)
    mixbox_dict['id'] = str(result.inserted_id)  # Assign the generated MongoDB ID to 'id'
    mixbox_dict.pop('_id', None)  # Remove the MongoDB '_id' if not needed elsewhere
    return mixbox_dict


# Retrieve all MixBoxes
@router.get("/", response_model=List[MixBox])
def get_all_mixboxes():
    mixboxes = list(collection.find())
    return [convert_object_id(mixbox) for mixbox in mixboxes]
def convert_object_id(mixbox):
    mixbox['id'] = str(mixbox['_id'])
    del mixbox['_id']  # Optionally delete the original '_id' if you want to clean it up
    return mixbox

@router.get("/{mixbox_id}", response_model=MixBox)
def get_mixbox(mixbox_id: str):
    mixbox = collection.find_one({"_id": ObjectId(mixbox_id)})
    if not mixbox:
        raise HTTPException(status_code=404, detail="MixBox not found")
    return convert_object_id(mixbox)


# Update an entire MixBox
@router.put("/{mixbox_id}", response_model=MixBox)
def update_mixbox(mixbox_id: str, mixbox: MixBox):
    result = collection.replace_one({"_id": ObjectId(mixbox_id)}, mixbox.dict(by_alias=True))
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="MixBox not found")
    return get_mixbox(mixbox_id)

# Partially update a MixBox
@router.patch("/{mixbox_id}", response_model=MixBox)
def partial_update_mixbox(mixbox_id: str, mixbox: MixBox):
    update_data = {k: v for k, v in mixbox.dict(by_alias=True).items() if v is not None}
    result = collection.update_one({"_id": ObjectId(mixbox_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="MixBox not found")
    return get_mixbox(mixbox_id)

# Delete a MixBox
@router.delete("/{mixbox_id}", status_code=204)
def delete_mixbox(mixbox_id: str):
    result = collection.delete_one({"_id": ObjectId(mixbox_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="MixBox not found")
    return {"message": "MixBox deleted successfully"}
