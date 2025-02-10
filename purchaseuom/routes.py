from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import PurchaseUOM, PurchaseUOMPost
from .utils import get_purchaseuom_collection

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_purchaseuom_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchaseuomId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_purchaseuom_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchaseuomId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"UO{counter_value:03d}"


# Function to get the current date and time with timezone as a datetime object
def get_current_date_and_time(timezone: str = "Asia/Kolkata") -> datetime:
    try:
        # Set the specified timezone
        specified_timezone = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    
    # Get the current time in the specified timezone and make it timezone-aware
    now = datetime.now(specified_timezone)
    
    return {
        "datetime": now  # Return the ISO 8601 formatted datetime string
    }
@router.post("/", response_model=str)
async def create_purchaseuom(purchaseuom: PurchaseUOMPost):
    # Check if the collection is empty
    if get_purchaseuom_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_purchaseuom_data = purchaseuom.dict()
    new_purchaseuom_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_purchaseuom_collection().insert_one(new_purchaseuom_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[PurchaseUOM])
async def get_all_purchaseuom():
    purchaseuoms = list(get_purchaseuom_collection().find())
    formatted_purchaseuoms = [
        {**purchaseuom, "purchaseuomId": str(purchaseuom["_id"])} for purchaseuom in purchaseuoms
    ]
    return [PurchaseUOM(**purchaseuom) for purchaseuom in formatted_purchaseuoms]

@router.get("/{purchaseuom_id}", response_model=PurchaseUOM)
async def get_purchaseuom_by_id(purchaseuom_id: str):
    purchaseuom = get_purchaseuom_collection().find_one({"_id": ObjectId(purchaseuom_id)})
    if purchaseuom:
        purchaseuom["purchaseuomId"] = str(purchaseuom["_id"])
        return PurchaseUOM(**purchaseuom)
    else:
        raise HTTPException(status_code=404, detail="PurchaseUOM not found")

@router.put("/{purchaseuom_id}")
async def update_purchaseuom(purchaseuom_id: str, purchaseuom: PurchaseUOMPost):
    updated_purchaseuom = purchaseuom.dict(exclude_unset=True)
    result = get_purchaseuom_collection().update_one({"_id": ObjectId(purchaseuom_id)}, {"$set": updated_purchaseuom})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseUOM not found")
    return {"message": "PurchaseUOM updated successfully"}

@router.patch("/{purchaseuom_id}")
async def patch_purchaseuom(purchaseuom_id: str, purchaseuom_patch: PurchaseUOMPost):
    existing_purchaseuom = get_purchaseuom_collection().find_one({"_id": ObjectId(purchaseuom_id)})
    if not existing_purchaseuom:
        raise HTTPException(status_code=404, detail="PurchaseUOM not found")

    updated_fields = {key: value for key, value in purchaseuom_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_purchaseuom_collection().update_one({"_id": ObjectId(purchaseuom_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update PurchaseUOM")

    updated_purchaseuom = get_purchaseuom_collection().find_one({"_id": ObjectId(purchaseuom_id)})
    updated_purchaseuom["_id"] = str(updated_purchaseuom["_id"])
    return updated_purchaseuom

@router.delete("/{purchaseuom_id}")
async def delete_purchaseuom(purchaseuom_id: str):
    result = get_purchaseuom_collection().delete_one({"_id": ObjectId(purchaseuom_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseUOM not found")
    return {"message": "PurchaseUOM deleted successfully"}
