from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import PurchaseSubcategory, PurchaseSubcategoryPost
from .utils import get_purchasesubcategory_collection

router = APIRouter()
purchase_category_counter = 0

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
def get_next_counter_value():
    counter_collection = get_purchasesubcategory_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchasesubcategoryId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_purchasesubcategory_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchasesubcategoryId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PS{counter_value:03d}"

@router.post("/", response_model=str)
async def create_purchasesubcategory(purchasesubcategory: PurchaseSubcategoryPost):
    # Check if the collection is empty
    if get_purchasesubcategory_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_purchasesubcategory_data = purchasesubcategory.dict()
    new_purchasesubcategory_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_purchasesubcategory_collection().insert_one(new_purchasesubcategory_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[PurchaseSubcategory])
async def get_all_purchasesubcategory():
    purchasesubcategories = list(get_purchasesubcategory_collection().find())
    formatted_purchasesubcategory = []
    
    for purchasesubcategory in purchasesubcategories:
        # Directly convert the MongoDB _id field to purchasesubcategoryId
        purchasesubcategory["purchasesubcategoryId"] = str(purchasesubcategory["_id"])
        
        # Append the formatted PurchaseSubcategory object
        formatted_purchasesubcategory.append(PurchaseSubcategory(**purchasesubcategory))
    
    return formatted_purchasesubcategory


@router.get("/{purchasesubcategory_id}", response_model=PurchaseSubcategory)
async def get_purchasesubcategory_by_id(purchasesubcategory_id: str):
    purchasesubcategory = get_purchasesubcategory_collection().find_one({"_id": ObjectId(purchasesubcategory_id)})
    if purchasesubcategory:
        purchasesubcategory["purchasesubcategoryId"] = str(purchasesubcategory["_id"])
        return PurchaseSubcategory(**purchasesubcategory)
    else:
        raise HTTPException(status_code=404, detail="purchasesubcategory not found")

@router.put("/{purchasesubcategory_id}")
async def update_purchasesubcategory(purchasesubcategory_id: str, purchasesubcategory: PurchaseSubcategoryPost):
    updated_purchasesubcategory = purchasesubcategory.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_purchasesubcategory_collection().update_one({"_id": ObjectId(purchasesubcategory_id)}, {"$set": updated_purchasesubcategory})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="purchasesubcategory not found")
    return {"message": "purchasesubcategory updated successfully"}

@router.patch("/{purchasesubcategory_id}")
async def patch_purchasesubcategory(purchasesubcategory_id: str, purchasesubcategory_patch: PurchaseSubcategoryPost):
    existing_purchasesubcategory = get_purchasesubcategory_collection().find_one({"_id": ObjectId(purchasesubcategory_id)})
    if not existing_purchasesubcategory:
        raise HTTPException(status_code=404, detail="purchasesubcategory not found")

    updated_fields = {key: value for key, value in purchasesubcategory_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_purchasesubcategory_collection().update_one({"_id": ObjectId(purchasesubcategory_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update purchasesubcategory")

    updated_purchasesubcategory = get_purchasesubcategory_collection().find_one({"_id": ObjectId(purchasesubcategory_id)})
    updated_purchasesubcategory["_id"] = str(updated_purchasesubcategory["_id"])
    return updated_purchasesubcategory

@router.delete("/{purchasesubcategory_id}")
async def delete_purchasesubcategory(purchasesubcategory_id: str):
    result = get_purchasesubcategory_collection().delete_one({"_id": ObjectId(purchasesubcategory_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="purchasesubcategory not found")
    return {"message": "purchasesubcategory deleted successfully"}
