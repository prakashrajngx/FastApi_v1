from datetime import datetime
import math
from pyexpat import errors
from typing import Dict, List, Literal, Optional
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import UpdateOne
import pytz
from .models import Grn, GrnPost,ItemDetail
from .utils import get_grn_collection

router = APIRouter()

class ItemUpdate(BaseModel):
    itemId: Optional[str]=None
    nos: Optional[float] = Field(default=None)  # Allow nos to be None
    eachQuantity:Optional[float]=None
    receivedQuantity: Optional[float]=None
    damagedQuantity: Optional[float]=None
    unitPrice: Optional[float]=None
    befTaxDiscount:Optional[float]=None
    afTaxDiscount:Optional[float]=None
    befTaxDiscountAmount:Optional[float]=None
    afTaxDiscountAmount:Optional[float]=None
    discountAmount:Optional[float]=None
    purchasetaxName:Optional[float]=None
    taxAmount:Optional[float]=None
    sgst:Optional[float] = None
    cgst: Optional[float] = None
    igst: Optional[float] = None
    taxType: Optional[Literal["cgst_sgst", "igst"]] = None
    expiryDate: Optional[datetime] = Field(default=None)  # Optional expiryDate

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
    counter_collection = get_grn_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "grnId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_grn_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "grnId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"GR{counter_value:03d}"
# Custom rounding function
def custom_round(value: float) -> float:
    # Round up if the decimal part is 0.5 or higher, round down otherwise
    return math.floor(value + 0.5)

@router.post("/", response_model=str)
async def create_grn(grn: GrnPost):
    if get_grn_collection().count_documents({}) == 0:
        reset_counter()
    
    current_date_and_time = get_current_date_and_time()

    random_id = generate_random_id()
    new_grn_data = grn.dict()
    new_grn_data['randomId'] = random_id
    new_grn_data['createdDate'] = current_date_and_time['datetime']  # Add created date
    new_grn_data['grnDate'] = current_date_and_time['datetime']  # Add order date

    result = get_grn_collection().insert_one(new_grn_data)
    return str(result.inserted_id)

# @router.get("/items/status/{status}", response_model=List[Grn])
# async def get_grns_with_item_status(status: str):
#     """
#     Retrieve GRNs where at least one item has the specified status.
#     """
#     if status not in ["Returned"]:  # Only checking for 'Returned' status
#         raise HTTPException(status_code=400, detail="Invalid status filter")
    
#     grn_collection = get_grn_collection()
    
#     # Fetch GRNs where any item has the specified status
#     grns = list(grn_collection.find({"itemDetails.status": status}))
    
#     if not grns:
#         raise HTTPException(status_code=404, detail=f"No GRNs found with item status '{status}'")
    
#     # Filter items based on the provided status
#     filtered_grns = []
#     for grn in grns:
#         filtered_items = [
#             item for item in grn.get("itemDetails", [])
#             if item.get("status") == status
#         ]
#         if filtered_items:
#             # Add GRN id and replace itemDetails with filtered items
#             grn["grnId"] = str(grn["_id"])
#             grn["itemDetails"] = filtered_items
#             # Remove the _id field to prevent it from being exposed
#             grn.pop("_id", None)
#             filtered_grns.append(Grn(**grn))
    
#     if not filtered_grns:
#         raise HTTPException(status_code=404, detail=f"No items found with status '{status}'")

#     return filtered_grns
@router.get("/", response_model=List[Grn])
async def get_grn_by_day_filter(
    days_filterdate: Optional[int] = Query(None, title="Days filter", description="Filter based on days (30, 60, 90)"),
):
    """
    Get GRNs filtered by a date difference based on the provided days filter (e.g., 30, 60, 90 days).
    The `agingDay` is calculated as the difference between the current date and `grnDate`.
    If no filter is provided, all GRNs will be returned.
    """
    try:
        # Retrieve all GRNs from the collection
        grns = list(get_grn_collection().find())
    except errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=f"Invalid GRN ID format: {str(e)}")

    filtered_grns = []

    # Get the current date
    current_date = datetime.now()

    for grn in grns:
        grn["grnId"] = str(grn["_id"])  # Convert ObjectId to string for JSON response

        # Extract the `grnDate` from the document
        grn_date = grn.get("grnDate")

        if grn_date:
            # Calculate the difference in days between the current date and `grnDate`
            days_diff = (current_date - grn_date).days

            # Calculate the aging day
            aging_day = days_diff
            grn["agingDay"] = aging_day

            # Apply the filter based on the number of days (30, 60, 90, etc.)
            if days_filterdate is None or aging_day <= days_filterdate:
                filtered_grns.append(Grn(**grn))
        else:
            # If `grnDate` is not found, include the GRN in the result if no filter is provided
            if days_filterdate is None:
                filtered_grns.append(Grn(**grn))

    # Return all GRNs if no filter is applied
    return filtered_grns if filtered_grns else grns
@router.get("/status", response_model=List[Grn])
async def get_grns_by_status(status: str):
    grn_collection = get_grn_collection()
    
    # Fetch GRNs where the status matches the provided parameter
    grns = list(grn_collection.find({"status": status}))
    
    if not grns:
        raise HTTPException(status_code=404, detail=f"No GRNs found with status '{status}'")
    
    formatted_grns = []
    for grn in grns:
        grn["grnId"] = str(grn["_id"])  # Add GRN ID
        grn.pop("_id", None)  # Remove the _id field for security reasons
        formatted_grns.append(Grn(**grn))

    return formatted_grns


@router.get("/{grn_id}", response_model=Grn)
async def get_grn_by_id(grn_id: str):
    grn = get_grn_collection().find_one({"_id": ObjectId(grn_id)})
    if grn:
        grn["grnId"] = str(grn["_id"])
        return Grn(**grn)
    else:
        raise HTTPException(status_code=404, detail="Grn not found")
    


@router.put("/{grn_id}")
async def update_grn(grn_id: str, grn: GrnPost):
    updated_grn = grn.dict(exclude_unset=True)
    result = get_grn_collection().update_one({"_id": ObjectId(grn_id)}, {"$set": updated_grn})
    current_date_and_time = get_current_date_and_time()
    update_grn['lastUpdatedDate'] = current_date_and_time['datetime']
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Grn not found")
    return {"message": "Grn updated successfully"}

@router.patch("/{grn_id}")
async def patch_grn(grn_id: str, grn_patch: GrnPost):
    existing_grn = get_grn_collection().find_one({"_id": ObjectId(grn_id)})
    if not existing_grn:
        raise HTTPException(status_code=404, detail="Grn not found")

    updated_fields = {key: value for key, value in grn_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
        result = get_grn_collection().update_one({"_id": ObjectId(grn_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Grn")

    updated_grn = get_grn_collection().find_one({"_id": ObjectId(grn_id)})
    updated_grn["_id"] = str(updated_grn["_id"])
    return updated_grn

@router.delete("/{grn_id}")
async def delete_grn(grn_id: str):
    result = get_grn_collection().delete_one({"_id": ObjectId(grn_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Grn not found")
    return {"message": "Grn deleted successfully"}
@router.patch("/items/totals/{grn_id}")
async def patch_item_totals(
    grn_id: str,
    discountPrice: float,
    item_updates: List[ItemUpdate],
):
    grn_collection = get_grn_collection()
    grn = grn_collection.find_one({"_id": ObjectId(grn_id)})

    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    update_operations = []
    updated_items = []
    total_received_amount = 0
    total_discount = 0
    total_tax = 0
    current_datetime = get_current_date_and_time()["datetime"]  # Get the current date and time
    
    for item_update in item_updates:
        item_id = item_update.itemId
        existing_item = next((item for item in grn.get("itemDetails", []) if item["itemId"] == item_id), None)

        if not existing_item:
            raise HTTPException(status_code=404, detail=f"Item ID {item_id} not found in GRN")

        # Use existing values if not provided
        nos_update = item_update.nos or existing_item["nos"]
        each_quantity = item_update.eachQuantity or existing_item["eachQuantity"]
        damaged_quantity = item_update.damagedQuantity or existing_item["damagedQuantity"]
        unit_price = item_update.unitPrice or existing_item["unitPrice"]
        bef_tax_discount = item_update.befTaxDiscount or existing_item.get("befTaxDiscount", 0)
        af_tax_discount = item_update.afTaxDiscount or existing_item.get("afTaxDiscount", 0)
        tax_percentage = item_update.purchasetaxName or existing_item["purchasetaxName"]
        expiry_date = item_update.expiryDate or existing_item.get("expiryDate")  # Handles both null and valid dates

        # Calculate quantities
        received_quantity = nos_update * each_quantity
        net_quantity = received_quantity - damaged_quantity

        # Total price before discounts
        total_price_before_discount = net_quantity * unit_price

        # Before tax discount amount
        bef_discount_amount = (bef_tax_discount / 100) * total_price_before_discount
        total_price_after_bef_discount = total_price_before_discount - bef_discount_amount

        # Tax calculated on the price after before tax discount
        tax_amount = (tax_percentage / 100) * total_price_after_bef_discount

        # Split tax based on taxType
        if item_update.taxType == "cgst_sgst":
            sgst = cgst = tax_amount / 2
            igst = 0
        elif item_update.taxType == "igst":
            igst = tax_amount
            sgst = cgst = 0
        else:
            raise HTTPException(status_code=400, detail=f"Invalid taxType for item ID {item_id}")

        # After tax discount amount
        af_discount_amount = (af_tax_discount / 100) * (total_price_after_bef_discount + tax_amount)
        final_price = total_price_after_bef_discount + tax_amount - af_discount_amount

        # Update operation
        update_operations.append(
            UpdateOne(
                {"_id": ObjectId(grn_id), "itemDetails.itemId": item_id},
                {"$set": {
                    f"itemDetails.$.nos": nos_update,
                    f"itemDetails.$.eachQuantity": each_quantity,
                    f"itemDetails.$.receivedQuantity": received_quantity,
                    f"itemDetails.$.damagedQuantity": damaged_quantity,
                    f"itemDetails.$.unitPrice": unit_price,
                    f"itemDetails.$.totalPrice": round(total_price_before_discount, 2),
                    f"itemDetails.$.befTaxDiscount": bef_tax_discount,
                    f"itemDetails.$.afTaxDiscount": af_tax_discount,
                    f"itemDetails.$.befTaxDiscountAmount": round(bef_discount_amount, 2),
                    f"itemDetails.$.afTaxDiscountAmount": round(af_discount_amount, 2),
                    f"itemDetails.$.discountAmount": round(bef_discount_amount + af_discount_amount, 2),
                    f"itemDetails.$.purchasetaxName": tax_percentage,
                    f"itemDetails.$.taxAmount": round(tax_amount, 2),
                    f"itemDetails.$.finalPrice": round(final_price, 2),
                    f"itemDetails.$.sgst": round(sgst, 2),
                    f"itemDetails.$.cgst": round(cgst, 2),
                    f"itemDetails.$.igst": round(igst, 2),
                    f"itemDetails.$.expiryDate": expiry_date,
                }}
            )
        )

        updated_items.append({
            "itemId": item_id,
            "receivedQuantity": received_quantity,
            "damagedQuantity": damaged_quantity,
            "unitPrice": unit_price,
            "totalPrice": total_price_before_discount,
            "befTaxDiscount": bef_tax_discount,
            "afTaxDiscount": af_tax_discount,
            "befTaxDiscountAmount": round(bef_discount_amount, 2),
            "afTaxDiscountAmount": round(af_discount_amount, 2),
            "discountAmount": round(bef_discount_amount + af_discount_amount, 2),
            "purchasetaxName": tax_percentage,
            "taxAmount": round(tax_amount, 2),
            "finalPrice": round(final_price, 2),
            "sgst": round(sgst, 2),
            "cgst": round(cgst, 2),
            "igst": round(igst, 2),
            "expiryDate": expiry_date,
        })

    if not update_operations:
        raise HTTPException(status_code=400, detail="No valid items provided for update")

    # Execute bulk write operation
    result = grn_collection.bulk_write(update_operations)

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No items were updated")

    # Update GRN document totals
    total_received_amount = sum(item['finalPrice'] for item in updated_items)
    total_discount = sum(item['discountAmount'] for item in updated_items)
    total_tax = sum(item['taxAmount'] for item in updated_items)

    if grn.get("status") != "GrnChecked":
        total_received_amount -= discountPrice
        total_discount += discountPrice
       # Apply custom rounding to the totalReceivedAmount
    total_received_amount = custom_round(total_received_amount)

    grn_collection.update_one(
        {"_id": ObjectId(grn_id)},
        {
            "$set": {
                "totalReceivedAmount": round(total_received_amount, 2),
                "discountPrice": round(discountPrice, 2),
                "totalDiscount": round(total_discount, 2),
                "totalTax": round(total_tax, 2),
                "status": "GrnChecked",
                "lastUpdatedDate": current_datetime,  # Add lastUpdatedDate to GRN document
            }
        }
    )

    return {
        "updatedItems": updated_items,
        "totalReceivedAmount": round(total_received_amount, 2),
        "totalDiscount": round(total_discount, 2),
        "totalTax": round(total_tax, 2),
    }

@router.patch("/items/status/{grn_id}")
async def update_item_status(grn_id: str, item_statuses: Dict[str, str]):
    """
    Update the status of multiple items in a GRN.
    """
    grn_collection = get_grn_collection()  # Access your GRN collection

    # Check if the GRN document exists
    grn = grn_collection.find_one({"_id": ObjectId(grn_id)})
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    updated_items = []

    for item_id, status in item_statuses.items():
        # Check if the item exists in the GRN
        existing_item = next(
            (item for item in grn.get("itemDetails", []) if item["itemId"] == item_id),
            None
        )
        if not existing_item:
            raise HTTPException(status_code=404, detail=f"Item ID {item_id} not found in GRN")

        # Update the item status
        result = grn_collection.update_one(
            {"_id": ObjectId(grn_id), "itemDetails.itemId": item_id},
            {"$set": {f"itemDetails.$.status": status}}  # Update the item's status
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail=f"Failed to update status for item ID {item_id}")

        # Add the updated item to the response
        updated_items.append({"itemId": item_id, "status": status})

    return {"message": "Item statuses updated successfully", "updatedItems": updated_items}


@router.get("/from-date/", response_model=List[Grn])
async def get_grn_by_date(
    fromDate: Optional[datetime] = Query(None, description="From date"),
    toDate: Optional[datetime] = Query(None, description="To date"),
    vendorName: Optional[str] = Query(None, description="Vendor name to filter by"),
    status: Optional[str] = Query(None, description="GRN status"),
):
    """
    Get GRNs based on a date range, vendor name filter, and status filter.
    """
    query = {}

    # Handle date range if provided
    if fromDate and toDate:
        # Normalize dates to midnight UTC
        fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        toDate = toDate.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ensure fromDate <= toDate
        if fromDate > toDate:
            raise HTTPException(status_code=400, detail="fromDate cannot be after toDate.")

        query["grnDate"] = {
            "$gte": fromDate,
            "$lte": toDate
        }

    # Handle single date if only fromDate is provided
    elif fromDate:
        # Normalize to midnight UTC
        fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        query["grnDate"] = {"$eq": fromDate}

    # Vendor name filtering if provided
    if vendorName:
        query["vendorName"] = {"$regex": f"^{vendorName}", "$options": "i"}  # Case-insensitive search

    # Status filtering if provided
    if status:
        query["status"] = {"$regex": f"^{status}$", "$options": "i"}  # Case-insensitive exact match

    # Query MongoDB based on the constructed query
    grns = list(get_grn_collection().find(query))

    # No results found, return an empty list
    if not grns:
        raise HTTPException(status_code=404, detail="No GRN found with the given filters.")
    # Format the GRNs to return
    formatted_grns = []
    for grn in grns:
        grn["grnId"] = str(grn["_id"])  # Convert ObjectId to string
        formatted_grns.append(Grn(**grn))  # Create Grn object based on your model

    return formatted_grns

@router.patch("/invoiceupdate/{grn_id}")
async def patch_invoice_details(
    grn_id: str,
    invoiceDate: Optional[datetime] = Query(None),  # Optional invoice date as query parameter
    invoiceNo: Optional[str] = Query(None),         # Optional invoice number as query parameter
):
    grn_collection = get_grn_collection()
    grn = grn_collection.find_one({"_id": ObjectId(grn_id)})

    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    # Prepare the fields for update
    grn_update_fields = {}

    if invoiceDate:
        grn_update_fields["invoiceDate"] = invoiceDate
    if invoiceNo:
        grn_update_fields["invoiceNo"] = invoiceNo

    # Update the GRN document with the invoice fields and clear all others
    result = grn_collection.update_one(
        {"_id": ObjectId(grn_id)},
        {"$set": grn_update_fields}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No updates were made to the GRN")

    return {
        "invoiceDate": invoiceDate if invoiceDate else grn.get("invoiceDate"),
        "invoiceNo": invoiceNo if invoiceNo else grn.get("invoiceNo"),
    }
@router.get("/dayfilters", response_model=List[Grn])
async def get_grn_by_day_filter(
    days_filterdate: Optional[int] = Query(None, title="Days filter", description="Filter based on days (30, 60, 90)"),
):
    """
    Get GRNs filtered by a date difference based on the provided days filter (e.g., 30, 60, 90 days).
    The `agingDay` is calculated as the difference between the current date and `grnDate`.
    """
    try:
        # Retrieve all GRNs from the collection
        grns = list(get_grn_collection().find())
    except errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=f"Invalid GRN ID format: {str(e)}")

    filtered_grns = []

    # Get the current date
    current_date = datetime.now()

    for grn in grns:
        grn["grnId"] = str(grn["_id"])  # Convert ObjectId to string for JSON response

        # Extract the `grnDate` from the document
        grn_date = grn.get("grnDate")

        if grn_date:
            # Calculate the difference in days between the current date and `grnDate`
            days_diff = (current_date - grn_date).days

            # Calculate the aging day
            aging_day = days_diff
            grn["agingDay"] = aging_day

            # Apply the filter based on the number of days (30, 60, 90, etc.)
            if days_filterdate is None or aging_day <= days_filterdate:
                filtered_grns.append(Grn(**grn))

    # Return the filtered list of GRNs
    return filtered_grns
