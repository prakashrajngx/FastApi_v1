from datetime import datetime
import io
from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile
from bson import ObjectId
from fastapi.responses import StreamingResponse
import pytz
from .models import Business, BusinessPost # Import Business and BusinessPost models
from .utils import get_businessdetails_collection,get_image_collection  # Make sure this utility function is implemented

router = APIRouter()

# Helper functions for counter and randomId generation for businessId
def get_next_counter_value():
    counter_collection = get_businessdetails_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "businessId"},
        {"$inc": {"sequence_value": 1}},  # Increment counter
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_businessdetails_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "businessId"},
        {"$set": {"sequence_value": 0}},  # Reset the counter
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"BD{counter_value:03d}"  # Business ID formatted like BD001, BD002, etc.


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

# Create business details
@router.post("/", response_model=Business)
async def create_business(business: BusinessPost):
    # Check if the collection is empty and reset the counter if it is
    if get_businessdetails_collection().count_documents({}) == 0:
        reset_counter()
    
    # Generate randomId (e.g., BD001, BD002)
    random_id = generate_random_id()

    current_date_and_time = get_current_date_and_time()

    # Prepare the business data, including the randomId
    new_business_data = business.dict()
    new_business_data['randomId'] = random_id
    new_business_data['status']= 'active'
    new_business_data['createdDate'] = current_date_and_time['datetime']  # Add created date

    # Insert the new business into MongoDB
    result = get_businessdetails_collection().insert_one(new_business_data)

    # Fetch the created business document from the database
    created_business = get_businessdetails_collection().find_one({"_id": result.inserted_id})
    created_business["businessId"] = str(created_business["_id"])  # Convert ObjectId to string
    
    return Business(**created_business)

# Get all businesses
@router.get("/", response_model=List[Business])
async def get_all_businesses():
    businesses = list(get_businessdetails_collection().find())
    formatted_businesses = []
    for business in businesses:
        business["businessId"] = str(business["_id"])  # Convert ObjectId to string
        formatted_businesses.append(Business(**business))  # Create Business model objects
    return formatted_businesses

# Get business by ID
@router.get("/{business_id}", response_model=Business)
async def get_business_by_id(business_id: str):
    business = get_businessdetails_collection().find_one({"_id": ObjectId(business_id)})
    if business:
        business["businessId"] = str(business["_id"])  # Convert ObjectId to string
        return Business(**business)  # Return Business model object
    else:
        raise HTTPException(status_code=404, detail="Business not found")

# Update business details (PUT)
@router.put("/{business_id}")
async def update_business(business_id: str, business: BusinessPost):
    updated_business = business.dict(exclude_unset=True)  # Exclude unset fields
    result = get_businessdetails_collection().update_one({"_id": ObjectId(business_id)}, {"$set": updated_business})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"message": "Business updated successfully"}

@router.patch("/{business_id}")
async def patch_businessdetails(business_id: str, business_patch: BusinessPost):
    existing_businessdetails = get_businessdetails_collection().find_one({"_id": ObjectId(business_id)})
    if not existing_businessdetails:
        raise HTTPException(status_code=404, detail="Businessdetails not found")

    updated_fields = {key: value for key, value in business_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
        result = get_businessdetails_collection().update_one({"_id": ObjectId(business_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Businessdetails")

    updated_business = get_businessdetails_collection().find_one({"_id": ObjectId(business_id)})
    updated_business["_id"] = str(updated_business["_id"])
    return updated_business

# Delete business by ID
@router.delete("/{business_id}")
async def delete_business(business_id: str):
    result = get_businessdetails_collection().delete_one({"_id": ObjectId(business_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return {"message": "Business deleted successfully"}

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...), custom_id: Optional[str] = None):
    try:
        # Read the contents of the uploaded file
        contents = await file.read()

        # Check if custom_id is provided, otherwise generate a new ObjectId
        if custom_id:
            custom_object_id = custom_id
        else:
            custom_object_id = str(ObjectId())

        # Insert the file contents into MongoDB with the custom ID
        result = get_image_collection().insert_one({
            "_id": custom_object_id,
            "filename": file.filename,
            "content": contents
        })

        # Construct the URL of the image
        image_url = f"/view/{custom_object_id}"

        return {"filename": file.filename, "id": custom_object_id, "imageUrl": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/view/{busines_id}")
async def get_photo(busines_id: str):
    try:
        # Retrieve document from MongoDB
        photo_document = get_image_collection().find_one({"_id": busines_id})

        if photo_document:
            # Retrieve content
            content = photo_document["content"]

            # Return StreamingResponse with the correct media type (image/jpeg or image/png, depending on your image)
            return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")  # Adjust media_type as per your image format

        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
