from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
import pytz
from .models import Apinvoice, ApinvoicePost,ItemDetail
from .utils import get_apinvoice_collection

router = APIRouter()


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

def get_next_counter_value() -> int:
    counter_collection = get_apinvoice_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "invoiceId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_apinvoice_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "invoiceId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id() -> str:
    counter_value = get_next_counter_value()
    return f"AP{counter_value:03d}"

@router.post("/", response_model=str)
async def create_apinvoice(apinvoice: ApinvoicePost):
    if get_apinvoice_collection().count_documents({}) == 0:
        reset_counter()
    
    random_id = generate_random_id()
    apinvoice_data = apinvoice.dict()
    current_date_and_time = get_current_date_and_time()

    apinvoice_data['randomId'] = random_id
    apinvoice_data['createdDate'] = current_date_and_time['datetime']  # Add created date
    apinvoice_data['apinvoiceDate'] = current_date_and_time['datetime']  # Add created time
    result = get_apinvoice_collection().insert_one(apinvoice_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[Apinvoice])
async def get_all_apinvoices():
    apinvoices = list(get_apinvoice_collection().find())
    formatted_apinvoices = []
    for apinvoice in apinvoices:
        apinvoice["invoiceId"] = str(apinvoice["_id"])
        formatted_apinvoices.append(Apinvoice(**apinvoice))
    return formatted_apinvoices

@router.get("/status", response_model=List[Apinvoice])
async def get_apinvoices_by_status(status: str):
    apinvoices = list(get_apinvoice_collection().find({"status": status}))
    
    if not apinvoices:
        raise HTTPException(status_code=404, detail=f"No AP Invoices found with status '{status}'")
    
    formatted_apinvoices = []
    for apinvoice in apinvoices:
        apinvoice["invoiceId"] = str(apinvoice["_id"])  # Convert ObjectId to string for response
        formatted_apinvoices.append(Apinvoice(**apinvoice))
    
    return formatted_apinvoices

@router.get("/{apinvoice_id}", response_model=Apinvoice)
async def get_apinvoice_by_id(apinvoice_id: str):
    apinvoice = get_apinvoice_collection().find_one({"_id": ObjectId(apinvoice_id)})
    if apinvoice:
        apinvoice["invoiceId"] = str(apinvoice["_id"])
        return Apinvoice(**apinvoice)
    else:
        raise HTTPException(status_code=404, detail="Apinvoice not found")

@router.put("/{apinvoice_id}", response_model=dict)
async def update_apinvoice(apinvoice_id: str, apinvoice: ApinvoicePost):
    updated_apinvoice = apinvoice.dict(exclude_unset=True)
    result = get_apinvoice_collection().update_one({"_id": ObjectId(apinvoice_id)}, {"$set": updated_apinvoice})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Apinvoice not found")
    return {"message": "Apinvoice updated successfully"}

@router.patch("/{apinvoice_id}", response_model=dict)
async def patch_apinvoice(apinvoice_id: str, apinvoice_patch: ApinvoicePost):
    existing_apinvoice = get_apinvoice_collection().find_one({"_id": ObjectId(apinvoice_id)})
    if not existing_apinvoice:
        raise HTTPException(status_code=404, detail="Apinvoice not found")

    updated_fields = {key: value for key, value in apinvoice_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
        result = get_apinvoice_collection().update_one({"_id": ObjectId(apinvoice_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Apinvoice")

    updated_apinvoice = get_apinvoice_collection().find_one({"_id": ObjectId(apinvoice_id)})
    updated_apinvoice["_id"] = str(updated_apinvoice["_id"])
    return updated_apinvoice

@router.delete("/{apinvoice_id}", response_model=dict)
async def delete_apinvoice(apinvoice_id: str):
    result = get_apinvoice_collection().delete_one({"_id": ObjectId(apinvoice_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Apinvoice not found")
    return {"message": "Apinvoice deleted successfully"}
@router.get("/from-date/", response_model=List[Apinvoice])
async def get_ap_by_date(
    fromDate: Optional[datetime] = Query(None, description="From date"),
    toDate: Optional[datetime] = Query(None, description="To date"),
    vendorName: Optional[str] = Query(None, description="Vendor name to filter by"),
    status: Optional[str] = Query(None, description="AP status"),
):
    """
    Get APs based on a date range, vendor name filter, and status filter.
    """
    query = {}

    # Handle date range for apDate
    if fromDate and toDate:
        # Normalize dates to midnight UTC and end of day for the time range
        fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        toDate = toDate.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ensure fromDate <= toDate
        if fromDate > toDate:
            raise HTTPException(status_code=400, detail="fromDate cannot be after toDate.")

        query["apinvoiceDate"] = {
            "$gte": fromDate,  # Start date
            "$lte": toDate     # End date
        }

    # Handle single date if only fromDate is provided
    elif fromDate:
        # Normalize to midnight UTC for exact match
        fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        query["apinvoiceDate"] = {"$eq": fromDate}

    # If no date is provided, skip the date query part
    else:
        # If only the status is provided, we will filter by status
        if not status and not vendorName:
            raise HTTPException(status_code=400, detail="At least one filter (status or date range) must be provided.")

    # Vendor name filtering if provided
    if vendorName:
        query["vendorName"] = {"$regex": f"^{vendorName}", "$options": "i"}  # Case-insensitive search for name starting with vendorName
    
    # Status filtering if provided
    if status:
        query["status"] = status  # Filter by status (e.g., "Pending")

    # Query MongoDB based on the constructed query
    aps = list(get_apinvoice_collection().find(query))

    # No 404 error, just return an empty list when no results are found
    if not aps:
        raise HTTPException(status_code=404, detail="No Ap found with the given filters.")

    # Format the Aps to return
    formatted_aps = []
    for ap in aps:
        ap["invoiceId"] = str(ap["_id"])  # Convert ObjectId to string
        formatted_aps.append(Apinvoice(**ap))  # Create an instance of Apinvoice model

    return formatted_aps
