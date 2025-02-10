from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import Apinvoicereturn, ApinvoicereturnPost
from .utils import get_apreturninvoice_collection  # Ensure you have this utility

router = APIRouter()

def get_next_return_counter_value() -> int:
    counter_collection = get_apreturninvoice_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "reverseinvoiceId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_return_counter():
    counter_collection = get_apreturninvoice_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "reverseinvoiceId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_return_random_id() -> str:
    counter_value = get_next_return_counter_value()
    return f"AR{counter_value:03d}"

@router.post("/", response_model=str)
async def create_apinvoice_return(apinvoice_return: ApinvoicereturnPost):
    if get_apreturninvoice_collection().count_documents({}) == 0:
        reset_return_counter()

    random_id = generate_return_random_id()
    apinvoice_return_data = apinvoice_return.dict()
    apinvoice_return_data['randomId'] = random_id

    result = get_apreturninvoice_collection().insert_one(apinvoice_return_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[Apinvoicereturn])
async def get_all_apinvoice_returns():
    apinvoice_returns = list(get_apreturninvoice_collection().find())
    formatted_apinvoice_returns = []
    for apinvoice_return in apinvoice_returns:
        apinvoice_return["reverseinvoiceId"] = str(apinvoice_return["_id"])
        formatted_apinvoice_returns.append(Apinvoicereturn(**apinvoice_return))
    return formatted_apinvoice_returns

@router.get("/{return_id}", response_model=Apinvoicereturn)
async def get_apinvoice_return_by_id(return_id: str):
    apinvoice_return = get_apreturninvoice_collection().find_one({"_id": ObjectId(return_id)})
    if apinvoice_return:
        apinvoice_return["reverseinvoiceId"] = str(apinvoice_return["_id"])
        return Apinvoicereturn(**apinvoice_return)
    else:
        raise HTTPException(status_code=404, detail="Apinvoice return not found")

@router.put("/{return_id}", response_model=dict)
async def update_apinvoice_return(return_id: str, apinvoice_return: ApinvoicereturnPost):
    updated_apinvoice_return = apinvoice_return.dict(exclude_unset=True)
    result = get_apreturninvoice_collection().update_one({"_id": ObjectId(return_id)}, {"$set": updated_apinvoice_return})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Apinvoice return not found")
    return {"message": "Apinvoice return updated successfully"}

@router.patch("/{return_id}", response_model=dict)
async def patch_apinvoice_return(return_id: str, apinvoice_return_patch: ApinvoicereturnPost):
    existing_apinvoice_return = get_apreturninvoice_collection().find_one({"_id": ObjectId(return_id)})
    if not existing_apinvoice_return:
        raise HTTPException(status_code=404, detail="Apinvoice return not found")

    updated_fields = {key: value for key, value in apinvoice_return_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_apreturninvoice_collection().update_one({"_id": ObjectId(return_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Apinvoice return")

    updated_apinvoice_return = get_apreturninvoice_collection().find_one({"_id": ObjectId(return_id)})
    updated_apinvoice_return["_id"] = str(updated_apinvoice_return["_id"])
    return updated_apinvoice_return

@router.delete("/{return_id}", response_model=dict)
async def delete_apinvoice_return(return_id: str):
    result = get_apreturninvoice_collection().delete_one({"_id": ObjectId(return_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Apinvoice return not found")
    return {"message": "Apinvoice return deleted successfully"}
