from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
import pytz
from .models import PurchaseCategory, PurchaseCategoryPost
from .utils import get_purchasecategory_collection

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_purchasecategory_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchasecategoryId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_purchasecategory_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchasecategoryId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PC{counter_value:03d}"


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
async def create_purchasecategory(purchasecategory: PurchaseCategoryPost):
    # Check if the collection is empty
    if get_purchasecategory_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()
    current_date=get_current_date_and_time()
    # Prepare data including randomId
    new_purchasecategory_data = purchasecategory.dict()
    new_purchasecategory_data['randomId'] = random_id
    new_purchasecategory_data['createdDate']=current_date['datetime']

    # Ensure subcategories is a list
    if isinstance(new_purchasecategory_data.get('subcategories'), str):
        new_purchasecategory_data['subcategories'] = [new_purchasecategory_data['subcategories']]

    # Insert into MongoDB
    result = get_purchasecategory_collection().insert_one(new_purchasecategory_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[PurchaseCategory])
async def get_all_purchasecategory():
    purchasecategories = list(get_purchasecategory_collection().find())
    formatted_purchasecategories = [
        {**pc, "purchasecategoryId": str(pc["_id"])} for pc in purchasecategories
    ]
    return [PurchaseCategory(**pc) for pc in formatted_purchasecategories]

@router.get("/{purchasecategory_id}", response_model=PurchaseCategory)
async def get_purchasecategory_by_id(purchasecategory_id: str):
    purchasecategory = get_purchasecategory_collection().find_one({"_id": ObjectId(purchasecategory_id)})
    if purchasecategory:
        purchasecategory["purchasecategoryId"] = str(purchasecategory["_id"])
        return PurchaseCategory(**purchasecategory)
    else:
        raise HTTPException(status_code=404, detail="PurchaseCategory not found")

@router.put("/{purchasecategory_id}")
async def update_purchasecategory(purchasecategory_id: str, purchasecategory: PurchaseCategoryPost):
    updated_purchasecategory = purchasecategory.dict(exclude_unset=True)

    # Ensure subcategories is a list
    if isinstance(updated_purchasecategory.get('subcategories'), str):
        updated_purchasecategory['subcategories'] = [updated_purchasecategory['subcategories']]
        updated_purchasecategory['lastUpdatedDate'] =  get_current_date_and_time()['datetime']
    result = get_purchasecategory_collection().update_one({"_id": ObjectId(purchasecategory_id)}, {"$set": updated_purchasecategory})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseCategory not found")
    return {"message": "PurchaseCategory updated successfully"}

@router.patch("/{purchasecategory_id}")
async def patch_purchasecategory(purchasecategory_id: str, purchasecategory_patch: PurchaseCategoryPost):
    existing_purchasecategory = get_purchasecategory_collection().find_one({"_id": ObjectId(purchasecategory_id)})
    if not existing_purchasecategory:
        raise HTTPException(status_code=404, detail="PurchaseCategory not found")

    updated_fields = {key: value for key, value in purchasecategory_patch.dict(exclude_unset=True).items() if value is not None}

    # Ensure subcategories is a list
    if 'subcategories' in updated_fields and isinstance(updated_fields['subcategories'], str):
        updated_fields['subcategories'] = [updated_fields['subcategories']]
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
    if updated_fields:
        result = get_purchasecategory_collection().update_one({"_id": ObjectId(purchasecategory_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update PurchaseCategory")

    updated_purchasecategory = get_purchasecategory_collection().find_one({"_id": ObjectId(purchasecategory_id)})
    updated_purchasecategory["_id"] = str(updated_purchasecategory["_id"])
    return updated_purchasecategory

@router.delete("/{purchasecategory_id}")
async def delete_purchasecategory(purchasecategory_id: str):
    result = get_purchasecategory_collection().delete_one({"_id": ObjectId(purchasecategory_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseCategory not found")
    return {"message": "PurchaseCategory deleted successfully"}
