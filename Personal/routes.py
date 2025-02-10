from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
import pytz
from .models import Personal, PersonalPost  # Assuming these models are created
from .utils import get_personaldetails_collection  # Utility to fetch the collection

router = APIRouter()

# Helper functions for counter and randomId generation for personalId
def get_next_counter_value():
    counter_collection = get_personaldetails_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "personalId"},
        {"$inc": {"sequence_value": 1}},  # Increment the counter value
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_personaldetails_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "personalId"},
        {"$set": {"sequence_value": 0}},  # Reset the counter
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PD{counter_value:03d}"  # Generate ID in the format PD001, PD002, etc.

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

# Create new personal details
@router.post("/", response_model=str)
async def create_personal(personal: PersonalPost):
    # Check if the collection is empty and reset the counter if it is
    if get_personaldetails_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId for personal ID
    random_id = generate_random_id()

    # Prepare data to be inserted
    new_personal_data = personal.dict()
    new_personal_data['randomId'] = random_id
    new_personal_data['createdDate'] = get_current_date_and_time()['datetime']
    new_personal_data['lastupdateDate'] = get_current_date_and_time()['datetime']
    new_personal_data['status'] = new_personal_data.get('status', 'active')  # Default to 'active'

    # Insert into MongoDB
    result = get_personaldetails_collection().insert_one(new_personal_data)
    return str(result.inserted_id)  # Return the MongoDB-generated ObjectId as a string

# Get all personal details
@router.get("/", response_model=List[Personal])
async def get_all_personal():
    personals = list(get_personaldetails_collection().find())
    formatted_personal = []
    for personal in personals:
        personal["personalId"] = str(personal["_id"])  # Convert ObjectId to string
        formatted_personal.append(Personal(**personal))  # Convert to Personal model
    return formatted_personal

# Get personal detail by ID
@router.get("/{personal_id}", response_model=Personal)
async def get_personal_by_id(personal_id: str):
    personal = get_personaldetails_collection().find_one({"_id": ObjectId(personal_id)})
    if personal:
        personal["personalId"] = str(personal["_id"])  # Convert ObjectId to string
        return Personal(**personal)  # Return Personal model object
    else:
        raise HTTPException(status_code=404, detail="Personal not found")

# Update personal details (PUT)
@router.put("/{personal_id}")
async def update_personal(personal_id: str, personal: PersonalPost):
    updated_personal = personal.dict(exclude_unset=True)  # Only update fields that are set
    result = get_personaldetails_collection().update_one({"_id": ObjectId(personal_id)}, {"$set": updated_personal})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Personal not found")
    return {"message": "Personal updated successfully"}

@router.patch("/{personal_id}")
async def patch_storagelocation(personal_id: str, personal_patch: PersonalPost):
    existing_personaldetails = get_personaldetails_collection().find_one({"_id": ObjectId(personal_id)})
    if not existing_personaldetails:
        raise HTTPException(status_code=404, detail="Personaldetails not found")

    updated_fields = {key: value for key, value in personal_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_personaldetails_collection().update_one({"_id": ObjectId(personal_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Personaldetails")

    updated_personal = get_personaldetails_collection().find_one({"_id": ObjectId(personal_id)})
    updated_personal["_id"] = str(updated_personal["_id"])
    updated_personal['lastupdateDate'] = updated_personal.get_current_date_and_time()['datetime']
    return updated_personal

# Delete personal details by ID
@router.delete("/{personal_id}")
async def delete_personal(personal_id: str):
    result = get_personaldetails_collection().delete_one({"_id": ObjectId(personal_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Personal not found")

    return {"message": "Personal deleted successfully"}
