from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import GrnReturn, GrnReturnPost, Item
from .utils import get_grn_return_collection

router = APIRouter()
def get_next_counter_value():
    counter_collection = get_grn_return_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "grnReturnId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_grn_return_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "grnReturnId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"GN{counter_value:03d}"

@router.post("/", response_model=str)
async def create_grn_return(grn_return: GrnReturnPost):
    try:
        if get_grn_return_collection().count_documents({}) == 0:
            reset_counter()
        
        random_id = generate_random_id()
        new_grn_return_data = grn_return.dict()
        new_grn_return_data['grnReturnId'] = random_id

        result = get_grn_return_collection().insert_one(new_grn_return_data)
        return str(result.inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[GrnReturn])
async def get_all_grn_returns():
    try:
        grn_returns = list(get_grn_return_collection().find())
        formatted_grn_returns = []
        for grn_return in grn_returns:
            grn_return["grnReturnId"] = str(grn_return["_id"])
            formatted_grn_returns.append(GrnReturn(**grn_return))
        return formatted_grn_returns
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{grnreturn_id}", response_model=GrnReturn)
async def get_grn_return_by_id(grnreturn_id: str):
    try:
        grnreturn = get_grn_return_collection().find_one({"_id": ObjectId(grnreturn_id)})
        if grnreturn:
            grnreturn["grnReturnId"] = str(grnreturn["_id"])
            return GrnReturn(**grnreturn)
        else:
            raise HTTPException(status_code=404, detail="GRN Return not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{grnreturn_id}")
async def update_grn_return(grn_return_id: str, grn_return: GrnReturnPost):
    try:
        updated_grn_return = grn_return.dict(exclude_unset=True)
        result = get_grn_return_collection().update_one({"_id": ObjectId(grn_return_id)}, {"$set": updated_grn_return})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="GRN Return not found")
        return {"message": "GRN Return updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/{grn_return_id}")
async def patch_grn_return(grn_return_id: str, grn_return_patch: GrnReturnPost):
    try:
        existing_grn_return = get_grn_return_collection().find_one({"_id": ObjectId(grn_return_id)})
        if not existing_grn_return:
            raise HTTPException(status_code=404, detail="GRN Return not found")

        updated_fields = {key: value for key, value in grn_return_patch.dict(exclude_unset=True).items() if value is not None}
        if updated_fields:
            result = get_grn_return_collection().update_one({"_id": ObjectId(grn_return_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update GRN Return")

        updated_grn_return = get_grn_return_collection().find_one({"_id": ObjectId(grn_return_id)})
        updated_grn_return["_id"] = str(updated_grn_return["_id"])
        return updated_grn_return
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{grn_return_id}")
async def delete_grn_return(grn_return_id: str):
    try:
        result = get_grn_return_collection().delete_one({"_id": ObjectId(grn_return_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="GRN Return not found")
        return {"message": "GRN Return deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
