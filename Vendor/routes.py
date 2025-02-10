import csv
from datetime import datetime
import io
from typing import List
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from bson import ObjectId
from fastapi.responses import StreamingResponse
import pytz
from .models import Vendor, VendorPost
from .utils import get_vendor_collection
import logging

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_vendor_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "vendorId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_vendor_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "vendorId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"VT{counter_value:03d}"

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
# Function to get the current date in a specific timezone
def get_current_date(timezone: str = "Asia/Kolkata") -> dict:
    # Set the specified timezone
    specified_timezone = pytz.timezone(timezone)
    
    # Get the current date and time in the specified timezone
    current_time = datetime.now(specified_timezone)
    
    # Return only the date part (year, month, day)
    return current_time.date()  # Returns just the current date


@router.post("/", response_model=str)
async def create_vendor(vendor_data: VendorPost):
    try:
        # Generate random vendor ID
        random_id = generate_random_id()
        
        current_date_and_time = get_current_date_and_time()
        # Prepare new vendor data including the randomId
        new_vendor_data = vendor_data.dict()
        new_vendor_data['randomId'] = random_id    
        new_vendor_data['createdDate'] = current_date_and_time['datetime']  # Add ISO 8601 datetime string

        # Insert the new vendor into MongoDB
        result = get_vendor_collection().insert_one(new_vendor_data)
        
        return str(result.inserted_id)
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[Vendor])
async def get_all_vendor():
    vendors = list(get_vendor_collection().find())
    formatted_vendors = []
    for vendor in vendors:
        vendor["vendorId"] = str(vendor["_id"])
        formatted_vendors.append(Vendor(**vendor))
    return formatted_vendors

@router.get("/limit", response_model=List[Vendor])
async def get_all_items(skip: int = Query(0, ge=0), limit: int = Query(50, le=5000)):
    try:
        cursor = get_vendor_collection().find().skip(skip).limit(limit)
        vendorlist = list(cursor)

        formatted_items = []
        for item in vendorlist:
            item["vendorId"] = str(item["_id"])
            formatted_items.append(Vendor(**item))

        return formatted_items

    except Exception as e:
        logging.error(f"Error occurred while fetching vendors: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{vendor_id}", response_model=Vendor)
async def get_vendor_by_id(vendor_id: str):
    vendor = get_vendor_collection().find_one({"_id": ObjectId(vendor_id)})
    if vendor:
        vendor["vendorId"] = str(vendor["_id"])
        return Vendor(**vendor)
    else:
        raise HTTPException(status_code=404, detail="Vendor not found")

@router.put("/{vendor_id}")
async def update_vendor(vendor_id: str, vendor_data: VendorPost):
    try:
        updated_vendor = vendor_data.dict(exclude_unset=True)
        current_date_and_time = get_current_date_and_time()
        updated_vendor['updatedDate'] = current_date_and_time['datetime']

        result = get_vendor_collection().replace_one({"_id": ObjectId(vendor_id)}, updated_vendor)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return {"message": "Vendor updated successfully"}
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/{vendor_id}")
async def patch_vendor(vendor_id: str, vendor_patch: VendorPost):
    try:
        existing_vendor = get_vendor_collection().find_one({"_id": ObjectId(vendor_id)})
        if not existing_vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        updated_fields = {key: value for key, value in vendor_patch.dict(exclude_unset=True).items() if value is not None}

        if updated_fields:
            updated_fields['updatedDate'] = get_current_date_and_time()['datetime']
            result = get_vendor_collection().update_one({"_id": ObjectId(vendor_id)}, {"$set": updated_fields})
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update vendor")

        updated_vendor = get_vendor_collection().find_one({"_id": ObjectId(vendor_id)})
        updated_vendor["_id"] = str(updated_vendor["_id"])
        return updated_vendor
    except Exception as e:
        logging.error(f"Error occurred while patching vendor: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: str):
    result = get_vendor_collection().delete_one({"_id": ObjectId(vendor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}

@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    contents = await file.read()
    decoded = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))

    vendors_to_insert = []
    current_date = get_current_date("Asia/Kolkata")
    for row in csv_reader:
        vendors_to_insert.append({
            "vendorName": row.get("vendorName"),
            "contactpersonName": row.get("contactpersonName"),
            "contactpersonPhone": row.get("contactpersonPhone"),
            "contactpersonEmail": row.get("contactpersonEmail"),
            "address": row.get("address"),
            "website": row.get("website"),
            "vendorType": row.get("vendorType"),
            "gstNumber": row.get("gstNumber"),
            "paymentTerms": row.get("paymentTerms"),
            "creditLimit": int(row.get("creditLimit")) if row.get("creditLimit") else None,
            "preferredpaymentMethod": row.get("preferredpaymentMethod"),
            "status": "active",  # Set status as 'active'
            "createdDate": current_date,  # Set the current time as a string in the desired format
            "notes": row.get("notes"),
            "country": row.get("country"),
            "state": row.get("state"),
            "city": row.get("city"),
            "postalCode": int(row.get("postalCode")) if row.get("postalCode") else None,
            "bankName": row.get("bankName"),
            "accountNumber": int(row.get("accountNumber")) if row.get("accountNumber") and row.get("accountNumber").isdigit() else None,
            "ifscCode": row.get("ifscCode"),
        })

    # Insert all vendors into MongoDB
    if vendors_to_insert:
        result = get_vendor_collection().insert_many(vendors_to_insert)
        return {"inserted_ids": [str(id) for id in result.inserted_ids]}
    
    return {"detail": "No vendors to insert"}

# @router.get("/export_csv", response_model=dict, operation_id="export_vendors_to_csv")
# async def export_all_vendors_to_csv():
#     try:
#         vendors = list(get_vendor_collection().find())
#         if not vendors:
#             raise HTTPException(status_code=404, detail="No vendors found")

#         csv_stream = io.StringIO()
#         csv_writer = csv.writer(csv_stream)

#         headers = [
#             'vendorName', 'contactpersonName', 'contactpersonPhone', 
#             'contactpersonEmail', 'address', 'website', 'vendorType', 
#             'gstNumber', 'paymentTerms', 'creditLimit', 'preferredpaymentMethod', 
#             'status', 'notes', 'country', 'state', 'city', 'postalCode', 
#             'bankName', 'accountNumber', 'ifscCode', 'createdDate', 'lastUpdatedDate'
#         ]
#         csv_writer.writerow(headers)

#         for vendor in vendors:
#             row = [
#                 vendor.get('vendorName', ''),
#                 vendor.get('contactpersonName', ''),
#                 vendor.get('contactpersonPhone', ''),
#                 vendor.get('contactpersonEmail', ''),
#                 vendor.get('address', ''),
#                 vendor.get('website', ''),
#                 vendor.get('vendorType', ''),
#                 vendor.get('gstNumber', ''),
#                 vendor.get('paymentTerms', ''),
#                 vendor.get('creditLimit', ''),
#                 vendor.get('preferredpaymentMethod', ''),
#                 vendor.get('status', ''),
#                 vendor.get('notes', ''),
#                 vendor.get('country', ''),
#                 vendor.get('state', ''),
#                 vendor.get('city', ''),
#                 vendor.get('postalCode', ''),
#                 vendor.get('bankName', ''),
#                 vendor.get('accountNumber', ''),
#                 vendor.get('ifscCode', ''),
#                 vendor.get('createdDate', ''),
#                 vendor.get('lastUpdatedDate', '')
#             ]
#             csv_writer.writerow(row)

#         csv_stream.seek(0)

#         response = StreamingResponse(
#             iter([csv_stream.getvalue().encode()]),
#             media_type="text/csv",
#             headers={"Content-Disposition": "attachment; filename=vendors.csv"}
#         )
#         return response
#     except Exception as e:
#         logging.error(f"Error occurred while exporting vendors to CSV: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

