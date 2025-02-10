from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import UpdateOne
from typing import List, Dict, Optional

import pytz
from .models import Outgoing, OutgoingPost
from .utils import get_outgoingpayment_collection


router = APIRouter()

def calculate_date_difference(invoice_date: str) -> int:
    # Parse the invoice_date assuming it's in "day-month-year" format (e.g., "01-12-2024")
    invoice_datetime = datetime.strptime(invoice_date, "%d-%m-%Y")  # Adjust format to match your date format
    current_datetime = datetime.now()
    delta = current_datetime - invoice_datetime
    return delta.days

class UpdatePaymentRequest(BaseModel):
    paymentMode:Optional[str] = Field(default=None)
    paymentMethod: Optional[str] = Field(default=None)
    neftNo: Optional[str] = Field(default=None)
    rtgsNo: Optional[str] = Field(default=None)
    cashVoucherNo: Optional[str] = Field(default=None)  # New field for voucher number for cash payments
    chequeNo: Optional[float] =Field(default=None)
    impsNo:Optional[str] = Field(default=None)
    upi:Optional[str] = Field(default=None)
    paymentCash: Optional[str] = Field(default=None)
    pettyCashAmount:Optional[float] = Field(default=None)
    hoCash:Optional[float] = Field(default=None)
    advanceAmount: Optional[float] = Field(default=None)
    partialAmount: Optional[float] = Field(default=None)
    fullPaymentAmount: Optional[float] = Field(default=None)
    paymentType: Optional[str] = Field(default=None)
    bankName:Optional[str] = Field(default=None)

class TaxDetail(BaseModel):
    taxName: str
    taxPercentage: float
    taxAmount: float

class ItemDetail(BaseModel):
    itemId: str
    purchasetaxName: float  # Tax percentage
    taxType: str
    sgst: float = 0
    cgst: float = 0
    igst: float = 0
    taxAmount: float = 0

class OutgoingResponse(BaseModel):
    taxes: List[TaxDetail]


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
def get_next_outgoing_counter_value():
    counter_collection = get_outgoingpayment_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "outgoingId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_outgoing_counter():
    counter_collection = get_outgoingpayment_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "outgoingId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_outgoing_random_id():
    counter_value = get_next_outgoing_counter_value()
    return f"OT{counter_value:03d}"

# Utility function to calculate the date difference in days
def calculate_date_difference(date_str: str) -> int:
    try:
        # Assuming the date is in dd-mm-yyyy format, change if necessary
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        current_date = datetime.now()
        # Calculate the difference in days
        return (current_date - date_obj).days
    except ValueError:
        # Return None if there's an issue with the date format
        return None

# Routes
@router.post("/", response_model=str)
async def create_outgoing(outgoing: OutgoingPost):
    if get_outgoingpayment_collection().count_documents({}) == 0:
        reset_outgoing_counter()

    random_id = generate_outgoing_random_id()
    new_outgoing_data = outgoing.dict()
    current_date_and_time = get_current_date_and_time()

    new_outgoing_data['randomId'] = random_id
    new_outgoing_data['createdDate'] = current_date_and_time['datetime']  # Add created date
    new_outgoing_data['lastUpdatedDate'] = current_date_and_time['datetime'] 
    result = get_outgoingpayment_collection().insert_one(new_outgoing_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[Outgoing])
async def get_all_outgoing(
    days_filterdate: Optional[int] = Query(None, title="Days filter", description="Filter based on days (30, 60, 90)")
):
    """
    Get all Outgoings. If days_filterdate is provided, filter by the date difference based on the days filter (e.g., 30, 60, 90 days).
    The intimationDays is calculated as (paymentTerms - days_diff), where days_diff is the difference between the current date and invoice date.
    """
    # Retrieve all outgoings from the collection
    outgoings = list(get_outgoingpayment_collection().find())
    filtered_outgoings = []

    # Get the current date
    current_date = datetime.now()

    for outgoing in outgoings:
     outgoing["outgoingId"] = str(outgoing["_id"])  # Convert ObjectId to string

    # Extract the invoiceDate from the document, which is already a datetime object
     invoice_date = outgoing.get("invoiceDate")
     payment_terms_str = outgoing.get("paymentTerms", "0")  # Assume paymentTerms is a string like "15 days"

     
     if invoice_date:
        # Calculate the date difference between the current date and the invoice date
        days_diff = (current_date - invoice_date).days

        # Extract numeric value from paymentTerms and convert to int, handle invalid cases
        digits = "".join(filter(str.isdigit, payment_terms_str))
        payment_terms = int(digits) if digits else 0  # Default to 0 if no digits are found

        # Subtract the days_diff from paymentTerms to get intimationDays
        intimation_days = payment_terms - days_diff

        # Store intimationDays in the outgoing data
        outgoing["intimationDays"] = intimation_days

        # If days_filterdate is provided, filter based on the provided value (e.g., 30, 60, or 90 days)
        if days_filterdate is None or intimation_days <= days_filterdate:
            filtered_outgoings.append(Outgoing(**outgoing))
     else:
        # If no invoice_date, still include the outgoing if no days_filterdate is applied
        if days_filterdate is None:
            filtered_outgoings.append(Outgoing(**outgoing))


    # Return the filtered list of outgoings (or all if no filter is applied)
    return filtered_outgoings

@router.get("/{outgoing_id}", response_model=Outgoing)
async def get_outgoing_by_id(outgoing_id: str):
    outgoing = get_outgoingpayment_collection().find_one({"_id": ObjectId(outgoing_id)})
    if outgoing:
        outgoing["outgoingId"] = str(outgoing["_id"])
        return Outgoing(**outgoing)
    else:
        raise HTTPException(status_code=404, detail="Outgoing document not found")

@router.put("/{outgoing_id}")
async def update_outgoing(outgoing_id: str, outgoing: OutgoingPost):
    updated_outgoing = outgoing.dict(exclude_unset=True)
    result = get_outgoingpayment_collection().update_one({"_id": ObjectId(outgoing_id)}, {"$set": updated_outgoing})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Outgoing document not found")
    return {"message": "Outgoing document updated successfully"}

@router.patch("/{outgoing_id}")
async def patch_outgoing(outgoing_id: str, outgoing_patch: OutgoingPost):
    existing_outgoing = get_outgoingpayment_collection().find_one({"_id": ObjectId(outgoing_id)})
    if not existing_outgoing:
        raise HTTPException(status_code=404, detail="Outgoing document not found")

    updated_fields = {key: value for key, value in outgoing_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
        result = get_outgoingpayment_collection().update_one({"_id": ObjectId(outgoing_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update Outgoing document")

    updated_outgoing = get_outgoingpayment_collection().find_one({"_id": ObjectId(outgoing_id)})
    updated_outgoing["_id"] = str(updated_outgoing["_id"])
    return updated_outgoing

@router.delete("/{outgoing_id}")
async def delete_outgoing(outgoing_id: str):
    result = get_outgoingpayment_collection().delete_one({"_id": ObjectId(outgoing_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Outgoing document not found")
    return {"message": "Outgoing document deleted successfully"}
@router.patch("/{outgoing_id}/payment")
async def update_outgoing_payment(
    outgoing_id: str,
    payment_info: UpdatePaymentRequest
):
    outgoing_collection = get_outgoingpayment_collection()
    outgoing = outgoing_collection.find_one({"_id": ObjectId(outgoing_id)})

    if not outgoing:
        raise HTTPException(status_code=404, detail="Outgoing document not found")
    
    # Store current date and time
    outgoing['lastUpdatedDate'] = get_current_date_and_time()['datetime']
    outgoing['paymentDate'] = get_current_date_and_time()['datetime']

    # Initialize payment amounts if they are None
    outgoing['advanceAmount'] = outgoing.get('advanceAmount', 0.0) or 0.0
    outgoing['partialAmount'] = outgoing.get('partialAmount', 0.0) or 0.0
    outgoing['fullPaymentAmount'] = outgoing.get('fullPaymentAmount', 0.0) or 0.0
    total_payable_amount = outgoing.get('totalPayableAmount', 0.0) or 0.0

    # Store the selected paymentMode: Bank or Cash
    outgoing['paymentMode'] = payment_info.paymentMode  # Store the selected mode

    # Handle Bank Payment Mode
    if payment_info.paymentMode == "Bank":
        outgoing['paymentMethod'] = payment_info.paymentMethod or outgoing.get('paymentMethod')

        # Handle payment method-specific fields for Bank
        if payment_info.paymentMethod == "neft":
            outgoing['neftNo'] = payment_info.neftNo
        elif payment_info.paymentMethod == "rtgs":
            outgoing['rtgsNo'] = payment_info.rtgsNo
        elif payment_info.paymentMethod == "imps":
            outgoing['impsNo'] = payment_info.impsNo
        elif payment_info.paymentMethod == "upi":
            outgoing['upi'] = payment_info.upi
        else:
            raise HTTPException(status_code=400, detail="Invalid payment method for Bank")  # Handle invalid method

        # Update bank name if provided
        if payment_info.bankName:
            outgoing['bankName'] = payment_info.bankName

        # Clear cash-related fields for Bank payments
        outgoing['pettyCashAmount'] = None
        outgoing['hoCash'] = None

    # Handle Cash Payment Mode
    elif payment_info.paymentMode == "Cash":
        outgoing['paymentMethod'] = payment_info.paymentMethod or outgoing.get('paymentMethod')

        # Handle cash payment method: Petty Cash or HO Cash
        if payment_info.paymentMethod == "pettyCash":
            outgoing['pettyCashAmount'] = payment_info.pettyCashAmount or 0.0
        elif payment_info.paymentMethod == "hoCash":
            outgoing['hoCash'] = payment_info.hoCash or 0.0
        else:
            raise HTTPException(status_code=400, detail="Invalid payment method for Cash")  # Handle invalid method

        # Clear bank-related fields for Cash payments
        outgoing['neftNo'] = None
        outgoing['rtgsNo'] = None
        outgoing['impsNo'] = None
        outgoing['upi'] = None
        outgoing['bankName'] = None  # Clear bankName if cash payment is made

    # Handle payment type (Full, Advance, Partial) and payment status
    if payment_info.paymentType == "full":
        outgoing['fullPaymentAmount'] = payment_info.fullPaymentAmount or outgoing['fullPaymentAmount']
        outgoing['partialAmount'] = 0.0  # Clear partial amount
        outgoing['advanceAmount'] = 0.0  # Clear advance amount
        outgoing['totalPayableAmount'] = 0.0
        outgoing['status'] = "Fully Paid"

    elif payment_info.paymentType == "partial":
        outgoing['partialAmount'] = payment_info.partialAmount or outgoing['partialAmount']
        outgoing['totalPayableAmount'] = total_payable_amount - outgoing['partialAmount']
        outgoing['status'] = "Partially Paid"

    elif payment_info.paymentType == "advance":
        outgoing['advanceAmount'] = payment_info.advanceAmount or outgoing['advanceAmount']
        outgoing['totalPayableAmount'] = total_payable_amount - outgoing['advanceAmount']
        outgoing['status'] = "Advance Paid"

    outgoing_collection.update_one({"_id": ObjectId(outgoing_id)}, {"$set": outgoing})

    return {
        "message": f"{payment_info.paymentMode.capitalize()} payment applied successfully.",
        "pendingAmount": outgoing['totalPayableAmount'],
        "totalPayableAmount": total_payable_amount,
        "partialAmount": outgoing['partialAmount'],
        "fullPaymentAmount": outgoing['fullPaymentAmount'],
        "advanceAmount": outgoing['advanceAmount'],
        "paymentType": payment_info.paymentType,
        "status": outgoing['status']
    }

@router.get("/{outgoing_id}/tax-details", response_model=OutgoingResponse)
async def get_outgoing_tax_details(outgoing_id: str):
    outgoing = get_outgoingpayment_collection().find_one({"_id": ObjectId(outgoing_id)})
    if not outgoing:
        raise HTTPException(status_code=404, detail="Outgoing document not found")

    # Initialize a list to hold the tax details
    tax_details = []

    # Iterate through item details to process taxes
    for item in outgoing["itemDetails"]:
        tax_type = item["taxType"]
        tax_percentage = item["purchasetaxName"]

        if tax_type == "cgst_sgst":
            sgst = item.get("sgst", 0)
            cgst = item.get("cgst", 0)
            # Add SGST and CGST to tax details
            tax_details.append(TaxDetail(taxName=f"SGST({tax_percentage / 2}%)", taxPercentage=tax_percentage / 2, taxAmount=sgst))
            tax_details.append(TaxDetail(taxName=f"CGST({tax_percentage / 2}%)", taxPercentage=tax_percentage / 2, taxAmount=cgst))

            # Add IGST with 0 for each set of SGST/CGST
            tax_details.append(TaxDetail(taxName="IGST(0%)", taxPercentage=0, taxAmount=0))

        elif tax_type == "igst":
            igst = item.get("igst", 0)
            # Add IGST with the actual value
            tax_details.append(TaxDetail(taxName=f"IGST({tax_percentage}%)", taxPercentage=tax_percentage, taxAmount=igst))

            # Add SGST and CGST with 0 if IGST is applied
            tax_details.append(TaxDetail(taxName="SGST(0%)", taxPercentage=0, taxAmount=0))
            tax_details.append(TaxDetail(taxName="CGST(0%)", taxPercentage=0, taxAmount=0))

        else:
            # Handle other tax types if present
            tax_amount = item.get("taxAmount", 0)
            tax_details.append(TaxDetail(taxName=f"{tax_type.upper()}({tax_percentage}%)", taxPercentage=tax_percentage, taxAmount=tax_amount))

    return OutgoingResponse(taxes=tax_details)

@router.get("/dayfilters", response_model=List[Outgoing])
async def get_outgoing_by_day_filter(
    days_filterdate: Optional[int] = Query(None, title="Days filter", description="Filter based on days (30, 60, 90)")
):
    """
    Get Outgoings filtered by a date difference based on the provided days filter (e.g., 30, 60, 90 days).
    The intimationDays is calculated as (paymentTerms - days_diff), where days_diff is the difference between the current date and invoice date.
    """
    # Retrieve all outgoings from the collection
    outgoings = list(get_outgoingpayment_collection().find())
    filtered_outgoings = []

    # Get the current date
    current_date = get_current_date_and_time()["datetime"]

    for outgoing in outgoings:
        outgoing["outgoingId"] = str(outgoing["_id"])  # Convert ObjectId to string

        # Extract the invoiceDate from the document, which is already a datetime object
        invoice_date = outgoing.get("invoiceDate")
        payment_terms = outgoing.get("paymentTerms", 0)  # Assume paymentTerms is in days, e.g., 20, 30, 60, 90

        if invoice_date:
            # Calculate the date difference between the current date and the invoice date
            days_diff = (current_date - invoice_date).days

            # Subtract the days_diff from paymentTerms to get intimationDays
            intimation_days = payment_terms - days_diff

            # Store intimationDays in the outgoing data
            outgoing["intimationDays"] = intimation_days

            # Filter based on the provided filter value (e.g., 30, 60, or 90 days)
            # Include outgoings if intimationDays is less than or equal to the filter value
            if days_filterdate is None or intimation_days <= days_filterdate:
                filtered_outgoings.append(Outgoing(**outgoing))

    # Return the filtered list of outgoings
    return filtered_outgoings

@router.get("/paymentdatefilters", response_model=List[Outgoing])
async def get_outgoing_by_payment_date_filter(
    days_filterdate: Optional[int] = Query(None, title="Days filter", description="Filter based on days (30, 60, 90)"),
):
    """
    Get Outgoings filtered by the difference between the current date and payment date.
    The filter is applied based on the number of days between the current date and payment date.
    """
    # Retrieve all outgoings from the collection
    outgoings = list(get_outgoingpayment_collection().find())
    filtered_outgoings = []

    # Get the current date
    current_date = get_current_date_and_time()["datetime"]

    for outgoing in outgoings:
        outgoing["outgoingId"] = str(outgoing["_id"])  # Convert ObjectId to string

        # Extract the paymentDate from the document
        payment_date = outgoing.get("paymentDate")

        if payment_date:
            # Ensure payment_date is a datetime object (convert if it's a string)
            if isinstance(payment_date, str):
                payment_date = datetime.fromisoformat(payment_date)

            # Calculate the difference in days between current date and payment date
            days_diff = (current_date - payment_date).days

            # Include outgoings if the difference is less than or equal to the filter value
            if days_filterdate is None or days_diff <= days_filterdate:
                filtered_outgoings.append(Outgoing(**outgoing))

    # Return the filtered list of outgoings
    return filtered_outgoings

@router.get("/outgoing-by-date/", response_model=List[Outgoing])
async def get_outgoing_by_date(
    fromDate: Optional[datetime] = Query(None, description="From date"),
    toDate: Optional[datetime] = Query(None, description="To date"),
    vendorName: Optional[str] = Query(None, description="Vendor name to filter by"),
    status: Optional[str] = Query(None, description="Outgoing status"),
    minTotalPayable: Optional[float] = Query(None, description="Minimum total payable amount to filter by"),
):
    """
    Get Outgoings based on a date range, vendor name filter, status filter, and total payable amount filter.
    """
    query = {}

    # Handle date range for invoiceDate
    if fromDate or toDate:
        # Normalize dates to midnight UTC for fromDate and toDate
        if fromDate:
            fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        if toDate:
            toDate = toDate.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ensure fromDate <= toDate
        if fromDate and toDate and fromDate > toDate:
            raise HTTPException(status_code=400, detail="fromDate cannot be after toDate.")

        # Add date range filters to query
        if fromDate and toDate:
            query["invoiceDate"] = {"$gte": fromDate, "$lte": toDate}
        elif fromDate:
            query["invoiceDate"] = {"$gte": fromDate}
        elif toDate:
            query["invoiceDate"] = {"$lte": toDate}

    # Vendor name filtering if provided
    if vendorName:
        query["vendorName"] = {"$regex": f"^{vendorName}", "$options": "i"}  # Case insensitive search for name starting with vendorName
    
    # Status filtering if provided
    if status:
        query["status"] = status  # Filter by status (e.g., "Pending")
    
    # Filter by totalPayable if provided
    if minTotalPayable is not None:
        if minTotalPayable == 0:
            query["totalPayableAmount"] = {"$gt": 0}  # Filter for totalPayable > 0
        else:
            query["totalPayableAmount"] = {"$gte": minTotalPayable}  # Filter for totalPayable >= minTotalPayable

    # Query MongoDB based on the constructed query
    outgoings = list(get_outgoingpayment_collection().find(query))

    # No 404 error, just return an empty list when no results are found
    if not outgoings:
        raise HTTPException(status_code=404, detail="No Outgoing found with the given filters.")

    # Format the Outgoings to return
    formatted_outgoings = []
    for outgoing in outgoings:
        outgoing["outgoingId"] = str(outgoing["_id"])  # Convert ObjectId to string
        
        # Ensure date format is correct (if it's needed)
        if "invoiceDate" in outgoing:
            outgoing["invoiceDate"] = outgoing["invoiceDate"]  # You can format it as needed

        formatted_outgoings.append(Outgoing(**outgoing))

    return formatted_outgoings


@router.get("/outgoing-by-vendor/", response_model=List[Outgoing])
async def get_outgoing_by_vendor(
    vendorName: Optional[str] = Query(None, description="Vendor name to filter by"),
):
    """
    Get Outgoings filtered by vendor name.
    """
    query = {}

    # Vendor name filtering if provided
    if vendorName:
        query["vendorName"] = {"$regex": f"^{vendorName}", "$options": "i"}  # Case insensitive search for name starting with vendorName

    # Query MongoDB based on the constructed query
    outgoings = list(get_outgoingpayment_collection().find(query))

    # No 404 error, just return an empty list when no results are found
    if not outgoings:
        return []  # Return an empty list when no matching outgoings are found

    # Format the Outgoings to return
    formatted_outgoings = []
    for outgoing in outgoings:
        outgoing["outgoingId"] = str(outgoing["_id"])  # Convert ObjectId to string
        formatted_outgoings.append(Outgoing(**outgoing))

    return formatted_outgoings
