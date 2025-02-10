from datetime import datetime
import io
import logging
import re
from typing import Dict, List, Optional
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from bson import ObjectId
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import pytz
from .models import PurchaseOrderState, PurchaseOrderPost,Item
from .utils import get_purchaseorder_collection,get_image_collection

router = APIRouter()

# Define the request model for the PATCH request
class ItemTotalsRequest(BaseModel):
    count:float
    eachQuantity:float
    quantity:float
    pendingCount: float  # Count of items
    pendingQuantity: float  # Each item's pending quantity (eachQuantity)
    pendingTotalQuantity: float  # Total quantity of items pending
    newPrice: float  # New price for the item
    receivedQuantity: Optional[float] = None  # Quantity of items received
    damagedQuantity: Optional[float] = None  # Quantity of items damaged
    befTaxDiscount: Optional[float] = None  # Discount before tax
    afTaxDiscount: Optional[float] = None  # Discount after tax
    taxPercentage: Optional[float] = 0  # Tax percentage on the item
    taxType: str = "cgst_sgst"  # Tax type to apply (cgst_sgst or igst)
    status:str
    invoiceDate:datetime
    invoiceNo:str

class ItemPatch(BaseModel):
    itemId: str  # Item ID that needs to be updated
    pendingCount: Optional[float] = None  # Pending count to be updated
    pendingQuantity: Optional[float] = None  # Pending quantity to be updated
    damagedQuantity: Optional[float] = None  # Damaged quantity to be updated
    befTaxDisocunt : Optional[float] = None
    afTaxDisocunt : Optional[float] =None
class PurchaseOrderPatch(BaseModel):
    invoiceDate: Optional[datetime] = None  # Invoice date
    invoiceNo: Optional[str] = None  # Invoice number
    discountPrice: Optional[float] = None  # Discount on the total purchase order
    items: List[ItemPatch]  # List of item details to be patched
    
    
    
    
    
def get_current_date_and_time(timezone: str = "Asia/Kolkata") -> dict:
    try:
        # Get the pytz timezone object for the given timezone string.
        specified_timezone = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")
    
    # Get the current UTC time and localize it to UTC.
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    
    # Convert the UTC time to the specified timezone.
    now_local = now_utc.astimezone(specified_timezone)
    
    # Debug print: show the current time in the specified timezone.
    print(f"Current time in {timezone} is: {now_local.isoformat()}")
    
    # Return the ISO formatted string.
    return {"datetime": now_local.isoformat()}

# Function to parse the date from the query string
def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if date_str:
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected format is dd-MM-yyyy.")
    return None

def get_next_counter_value():
    counter_collection = get_purchaseorder_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchaseorderId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_purchaseorder_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchaseorderId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PO{counter_value:03d}"


@router.post("/", response_model=PurchaseOrderState)
async def create_purchaseorder(purchaseorder: PurchaseOrderPost):
    if get_purchaseorder_collection().count_documents({}) == 0:
        reset_counter()
    
    random_id = generate_random_id()
    new_purchaseorder_data = purchaseorder.dict()

    # Get the current date and time using the updated utility function
    current_date_and_time = get_current_date_and_time()

    # Automatically add the status and date/time fields in the backend
    new_purchaseorder_data['randomId'] = random_id
    new_purchaseorder_data['poStatus'] = 'Pending'  # Set the default status as 'Pending'
    new_purchaseorder_data['createdDate'] = current_date_and_time['datetime']  # Store as datetime
    new_purchaseorder_data['orderDate'] = current_date_and_time['datetime']  # Store as datetime

    # Insert the purchase order into the database
    result = get_purchaseorder_collection().insert_one(new_purchaseorder_data)

    # Fetch the created purchase order from the database
    created_purchaseorder = get_purchaseorder_collection().find_one({"_id": result.inserted_id})
    created_purchaseorder["purchaseOrderId"] = str(created_purchaseorder["_id"])  # Convert ObjectId to string
    
    return PurchaseOrderState(**created_purchaseorder)

# @router.get("/", response_model=List[PurchaseOrderState])
# async def get_all_purchaseorders():
#     purchaseorders = list(get_purchaseorder_collection().find())
#     formatted_purchaseorder = []
#     for purchaseorder in purchaseorders:
#         purchaseorder["purchaseOrderId"] = str(purchaseorder["_id"])
#         formatted_purchaseorder.append(PurchaseOrderState(**purchaseorder))
#     return formatted_purchaseorder

@router.get("/", response_model=List[PurchaseOrderState])
async def get_all_purchaseorders(item_name: str = Query(None, min_length=1, max_length=100)):
    # Initialize a list to store formatted purchase orders
    formatted_purchaseorders = []

    # If an item_name is provided, perform the search
    if item_name:
        # Define a case-insensitive regex pattern to match item names
        regex_pattern = re.compile(item_name, re.IGNORECASE)
        
        # Fetch all purchase orders from the collection
        purchaseorders = list(get_purchaseorder_collection().find())

        for purchaseorder in purchaseorders:
            # Check if any item name contains the search keyword
            if any(regex_pattern.search(item["itemName"]) for item in purchaseorder["items"]):
                purchaseorder["purchaseOrderId"] = str(purchaseorder["_id"])
                formatted_purchaseorders.append(PurchaseOrderState(**purchaseorder))
    else:
        # If no item_name is provided, return all purchase orders
        purchaseorders = list(get_purchaseorder_collection().find())

        for purchaseorder in purchaseorders:
            purchaseorder["purchaseOrderId"] = str(purchaseorder["_id"])
            formatted_purchaseorders.append(PurchaseOrderState(**purchaseorder))

    return formatted_purchaseorders

@router.get("/{purchaseorder_id}", response_model=PurchaseOrderState)
async def get_purchaseorder_by_id(purchaseorder_id: str):
    purchaseorder = get_purchaseorder_collection().find_one({"_id": ObjectId(purchaseorder_id)})
    if purchaseorder:
        purchaseorder["purchaseOrderId"] = str(purchaseorder["_id"])
        return PurchaseOrderState(**purchaseorder)
    else:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")

@router.put("/{purchaseorder_id}")
async def update_purchaseorder(purchaseorder_id: str, purchaseorder: PurchaseOrderPost):
    updated_purchaseorder = purchaseorder.dict(exclude_unset=True)
    current_date_and_time = get_current_date_and_time()
    updated_purchaseorder['lastUpdatedDate'] = current_date_and_time['datetime']
    
    result = get_purchaseorder_collection().update_one({"_id": ObjectId(purchaseorder_id)}, {"$set": updated_purchaseorder})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")
    return {"message": "PurchaseOrder updated successfully"}

@router.patch("/{purchaseorder_id}")
async def patch_purchaseorder(purchaseorder_id: str, purchaseorder_patch: PurchaseOrderPost):
    existing_purchaseorder = get_purchaseorder_collection().find_one({"_id": ObjectId(purchaseorder_id)})
    if not existing_purchaseorder:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")

    updated_fields = {key: value for key, value in purchaseorder_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        updated_fields['lastUpdatedDate'] = get_current_date_and_time()['datetime']
        result = get_purchaseorder_collection().update_one({"_id": ObjectId(purchaseorder_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update PurchaseOrder")

    updated_purchaseorder = get_purchaseorder_collection().find_one({"_id": ObjectId(purchaseorder_id)})
    updated_purchaseorder["_id"] = str(updated_purchaseorder["_id"])
    return updated_purchaseorder

@router.delete("/{purchaseorder_id}")
async def delete_purchaseorder(purchaseorder_id: str):
    result = get_purchaseorder_collection().delete_one({"_id": ObjectId(purchaseorder_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseOrder not found")
    return {"message": "PurchaseOrder deleted successfully"}
    
@router.get("/items/totals")
async def get_item_totals(
    pendingTotalQuantity: float = Query(..., description="Quantity of the item"),
    newPrice: float = Query(..., description="New price of the item"),
    befTaxDiscount: Optional[float] = Query(None, description="Discount percentage before tax on the item"),
    afTaxDiscount: Optional[float] = Query(None, description="Discount percentage after tax on the item"),
    taxPercentage: Optional[float] = Query(0, description="Tax percentage on the item"),
    taxType: str = Query("cgst_sgst", description="Type of tax to apply (cgst_sgst or igst)")
) -> Dict[str, float]:
    # Validate taxType
    if taxType not in {"cgst_sgst", "igst"}:
        return {"error": "Invalid taxType. Must be 'cgst_sgst' or 'igst'."}

    """
    Calculate the total price, discount (before and after tax), and tax split (SGST, CGST, and IGST) for the item 
    based on provided parameters.
    """

    # Handle empty discounts
    befTaxDiscount = befTaxDiscount if befTaxDiscount is not None else 0
    afTaxDiscount = afTaxDiscount if afTaxDiscount is not None else 0

    # Calculate the total price before any discount
    total_price_before_discount = pendingTotalQuantity * newPrice

    # Calculate the discount amount before tax
    bef_tax_discount_amount = total_price_before_discount * (befTaxDiscount / 100)
    total_price_after_bef_discount = total_price_before_discount - bef_tax_discount_amount

    # Initialize tax amounts
    sgst_amount = cgst_amount = igst_amount = 0

    # Calculate the tax amount based on the price after the before-tax discount
    if taxType == "cgst_sgst":
        # Split the tax percentage equally between SGST and CGST
        sgst_amount = total_price_after_bef_discount * (taxPercentage / 2 / 100)
        cgst_amount = total_price_after_bef_discount * (taxPercentage / 2 / 100)
        total_tax_amount = sgst_amount + cgst_amount
    elif taxType == "igst":
        # Apply the full tax percentage as IGST
        igst_amount = total_price_after_bef_discount * (taxPercentage / 100)
        total_tax_amount = igst_amount
    else:
        return {"error": "Invalid taxType. Choose either 'cgst_sgst' or 'igst'."}

    # Calculate the total price after adding the tax
    total_price_after_tax = total_price_after_bef_discount + total_tax_amount

    # Calculate the discount amount after tax
    af_tax_discount_amount = total_price_after_tax * (afTaxDiscount / 100)
    final_price = total_price_after_tax - af_tax_discount_amount

    # Calculate the total discount amount (before-tax and after-tax combined)
    total_discount_amount = bef_tax_discount_amount + af_tax_discount_amount

    return {
        "pendingTotalPrice": round(total_price_before_discount, 2),  # Total price before any discount
        "pendingBefTaxDiscountAmount": round(bef_tax_discount_amount, 2),  # Discount amount before tax
        "pendingAfTaxDiscountAmount": round(af_tax_discount_amount, 2),  # Discount amount after tax
        "pendingDiscountAmount": round(total_discount_amount, 2),  # Total discount applied
        "pendingTaxAmount": round(total_tax_amount, 2),  # Total tax applied
        "pendingSgst": round(sgst_amount, 2),  # SGST amount (if applicable)
        "pendingCgst": round(cgst_amount, 2),  # CGST amount (if applicable)
        "pendingIgst": round(igst_amount, 2),  # IGST amount (if applicable)
        "pendingFinalPrice": round(final_price, 2),  # Final price after all discounts and tax
    }
@router.post("/upload")
async def upload_photo(files: List[UploadFile] = File(...), custom_id: Optional[str] = None):
    try:
        if custom_id:
            custom_object_id = custom_id
        else:
            custom_object_id = str(ObjectId())

        photo_document = get_image_collection().find_one({"_id": custom_object_id})

        image_urls = photo_document.get("imageUrls", []) if photo_document else []
        image_contents = photo_document.get("imageContents", []) if photo_document else []

        for file in files:
            contents = await file.read()

            image_url = f"/view/{custom_object_id}/{len(image_urls)}"
            image_urls.append(image_url)
            image_contents.append(contents)

        if photo_document:
            get_image_collection().update_one(
                {"_id": custom_object_id},
                {"$set": {"imageUrls": image_urls, "imageContents": image_contents}}
            )
        else:
            get_image_collection().insert_one({
                "_id": custom_object_id,
                "filename": [file.filename for file in files],
                "imageUrls": image_urls,
                "imageContents": image_contents
            })

        return {"filenames": [file.filename for file in files], "id": custom_object_id, "imageUrls": image_urls}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/view/{photo_id}")
async def get_photo(photo_id: str, image_index: Optional[int] = None):
    try:
        photo_document = get_image_collection().find_one({"_id": photo_id})

        if photo_document:
            image_urls = photo_document.get("imageUrls", [])
            image_contents = photo_document.get("imageContents", [])

            if image_index is not None:
                if 0 <= image_index < len(image_urls):
                    content = image_contents[image_index]
                    return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")
                else:
                    raise HTTPException(status_code=404, detail="Image index out of bounds")
            else:
                image_list = [{"url": f"/view/{photo_id}?image_index={index}"} for index in range(len(image_urls))]
                return {"photo_id": photo_id, "images": image_list}

        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/from-date/", response_model=List[PurchaseOrderState])
async def get_purchaseorder_by_date(
    fromDate: Optional[datetime] = Query(None, description="From date"),
    toDate: Optional[datetime] = Query(None, description="To date"),
    vendorName: Optional[str] = Query(None, description="Vendor name to filter by"),
    status: Optional[str] = Query(None, description="Purchase order status (e.g., Pending)"),
):
    """
    Get Purchase orders  based on a date range, vendor name filter, and status filter.
    If no vendor name is provided, fetch all data based on the date range.
    If no status is provided, fetch all purchase orders with any status.
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
        
        query["orderDate"] = {
            "$gte": fromDate,
            "$lte": toDate
        }

    # Handle single date if only fromDate is provided
    elif fromDate:
        # Normalize to midnight UTC
        fromDate = fromDate.replace(hour=0, minute=0, second=0, microsecond=0)
        query["orderDate"] = {"$eq": fromDate}

    # Vendor name filtering if provided
    if vendorName:
        query["vendorName"] = {"$regex": f"^{vendorName}", "$options": "i"}  # Case-insensitive search

    # Status filtering if provided
    if status:
        query["poStatus"] = {"$regex": f"^{status}$", "$options": "i"}  # Case-insensitive exact match

    # Query MongoDB based on the constructed query
    purchases = list(get_purchaseorder_collection().find(query))

    # Handle case where no data is found
    if not purchases:
        raise HTTPException(status_code=404, detail="No purchase orders found with the given filters.")

    # Format the purchase orders to return
    formatted_purchaseorders = []
    for purchase in purchases:
        purchase["purchaseOrderId"] = str(purchase["_id"])  # Convert ObjectId to string
        formatted_purchaseorders.append(PurchaseOrderState(**purchase))

    return formatted_purchaseorders
@router.get("/sorted", response_model=List[PurchaseOrderState])
async def get_all_purchaseorders(
    sort_by_expected_delivery: Optional[str] = Query(None, title="Sort by Expected Delivery Date", description="Sort by expected delivery date: 'asc' or 'desc'"),
):
    """
    Get all purchase orders with expected delivery intimations and allow sorting by expected delivery date.
    """
    # Retrieve all purchase orders from the collection
    purchaseorders = list(get_purchaseorder_collection().find())

    formatted_purchaseorders = []
    current_date = datetime.now()

    for purchaseorder in purchaseorders:
        purchaseorder["purchaseOrderId"] = str(purchaseorder["_id"])  # Convert ObjectId to string
        order_date = purchaseorder.get("orderDate")
        expected_delivery_date = purchaseorder.get("expectedDeliveryDate")
        
        if expected_delivery_date:
            # Ensure expected_delivery_date is a datetime object
            expected_delivery_date = datetime.strptime(expected_delivery_date, "%Y-%m-%dT%H:%M:%S")

            # Calculate the days difference between current date and expected delivery date
            days_diff = (current_date - expected_delivery_date).days
            
            # Set the intimation based on the days difference
            if days_diff > 0:
                expected_delivery_intimation = f"Product overdue by {days_diff} days"
            elif days_diff == 0:
                expected_delivery_intimation = "Product is expected today"
            else:
                expected_delivery_intimation = f"Product expected in {abs(days_diff)} days"

            # Calculate intimation days (days from order date to expected delivery)
            if order_date:
                order_date = datetime.strptime(order_date, "%Y-%m-%dT%H:%M:%S")
                order_to_expected_delivery_days = (expected_delivery_date - order_date).days
                intimation_days = order_to_expected_delivery_days - days_diff  # Compare days
                purchaseorder["intimationDays"] = intimation_days
        else:
            expected_delivery_intimation = "No expected delivery date set"

        purchaseorder["expectedDeliveryIntimation"] = expected_delivery_intimation
        formatted_purchaseorders.append(PurchaseOrderState(**purchaseorder))

    # Sort by expected delivery date if the parameter is provided
    if sort_by_expected_delivery:
        reverse_sort = True if sort_by_expected_delivery == 'desc' else False
        formatted_purchaseorders.sort(key=lambda x: x.expectedDeliveryDate, reverse=reverse_sort)

    return formatted_purchaseorders
@router.patch("/receivedupdates/{purchaseOrderId}")
async def patch_received_count(purchaseOrderId: str, purchaseOrderPatch: Dict) -> Dict:
    existing_purchaseorder = get_purchaseorder_collection().find_one({"_id": ObjectId(purchaseOrderId)})

    if not existing_purchaseorder:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    # Initialize totals
    total_discount = 0
    total_amount_before_tax = 0
    total_tax = 0
    total_amount_after_tax = 0
    total_pending_discount = 0
    total_pending_tax = 0
    total_amount_pending_before_tax = 0
    total_amount_pending_after_tax = 0
    updated_items = []
    all_items_received = True

    # Apply overall PO discount from patch
    item_discount = purchaseOrderPatch.get('discountPrice', 0)
    existing_purchaseorder["discountPrice"] = item_discount

    item_pending_discount = purchaseOrderPatch.get('pendingDiscountAmount', 0)
    existing_purchaseorder["pendingDiscountAmount"] = item_pending_discount

    # Process each item in the patch
    for item_patch in purchaseOrderPatch.get('items', []):
        updated_item = next((i for i in existing_purchaseorder.get('items', []) if i['itemId'] == item_patch['itemId']), None)

        if updated_item:
            # Update item quantities and other fields
            updated_item['pendingCount'] = item_patch.get('pendingCount', updated_item.get('pendingCount', 0))
            updated_item['pendingQuantity'] = max(0, updated_item.get('pendingQuantity', 0) - item_patch.get('pendingQuantity', 0))
            updated_item['count'] = item_patch.get('pendingCount', updated_item.get('pendingCount', 0))
            updated_item['eachQuantity'] = item_patch.get('pendingQuantity', updated_item.get('pendingQuantity', 0))

            # Calculate total quantities
            pending_total_quantity = updated_item['pendingCount'] * updated_item['pendingQuantity']
            updated_item['pendingTotalQuantity'] = pending_total_quantity
            total_quantity = updated_item['count'] * updated_item['eachQuantity']
            updated_item['receivedQuantity'] = total_quantity

            # Handle damaged quantity
            damaged_quantity = item_patch.get('damagedQuantity', 0)
            updated_item['damagedQuantity'] = damaged_quantity
            final_quantity_for_storage = max(0, total_quantity - damaged_quantity)
            updated_item['quantity'] = final_quantity_for_storage

            # Set item status based on pending total quantity
            updated_item['status'] = "Received" if pending_total_quantity == 0 else "Pending"

            # Calculate price and discounts
            total_price = final_quantity_for_storage * updated_item.get('newPrice', 0)
            updated_item['totalPrice'] = total_price
            pending_total_price = pending_total_quantity * updated_item.get('newPrice', 0)
            updated_item['pendingTotalPrice'] = pending_total_price
            
            # Calculate discounts and taxes for received items

            # Before tax discount calculation
            bef_tax_discount = total_price * (updated_item.get('befTaxDiscount', 0) / 100)
            bef_discount_total = total_price - bef_tax_discount
            item_tax = bef_discount_total * (updated_item.get('taxPercentage', 0) / 100)

            # After tax discount calculation
            
            tax_after = total_price - item_tax
            af_tax_discount = tax_after * (updated_item.get('afTaxDiscount', 0) / 100)
            tax = item_tax

            # Calculate pending discounts and taxes
            bef_pending_tax_discount = pending_total_price * (updated_item.get('befTaxDiscount', 0) / 100)
            bef_pending_discount_total = pending_total_price - bef_pending_tax_discount
            item_pending_tax = bef_pending_discount_total * (updated_item.get('taxPercentage', 0) / 100)

            # Apply CGST/SGST or IGST tax
            item_cgst = item_sgst = item_igst = 0
            pending_cgst = pending_sgst = pending_igst = 0

            if updated_item['taxType'] == 'cgst_sgst':
                item_cgst = item_tax / 2
                item_sgst = item_tax / 2
                pending_cgst = item_pending_tax / 2
                pending_sgst = item_pending_tax / 2
            elif updated_item['taxType'] == 'igst':
                item_igst = item_tax
                pending_igst = item_pending_tax

            # Accumulate totals for order
            total_discount += bef_tax_discount if updated_item.get('befTaxDiscount', 0) > 0 else af_tax_discount
            total_amount_before_tax += total_price
            total_tax += item_tax
            total_amount_after_tax += bef_discount_total + item_tax

            total_amount_pending_before_tax += pending_total_price
            total_pending_tax += item_pending_tax
            total_amount_pending_after_tax += bef_pending_discount_total + item_pending_tax

            item_final_price = bef_discount_total + item_tax
            item_pending_final_price = bef_pending_discount_total + item_pending_tax
            
            # Updated item details for response
            updated_item['taxAmount'] = round(item_tax, 2)
            updated_item['pendingTaxAmount'] = round(item_pending_tax, 2)
            updated_item['befTaxDiscount'] = item_patch.get('befTaxDiscount', updated_item.get('befTaxDiscount', 0))
            updated_item['afTaxDiscount'] = item_patch.get('afTaxDiscount', updated_item.get('afTaxDiscount', 0))
            updated_item['befTaxDiscountAmount'] = round(bef_tax_discount, 2)
            updated_item['afTaxDiscountAmount'] = round(af_tax_discount, 2)
            updated_item['cgst'] = round(item_cgst, 2)
            updated_item['sgst'] = round(item_sgst, 2)
            updated_item['igst'] = round(item_igst, 2)
            updated_item['pendingBefTaxDiscountAmount'] = round(bef_pending_tax_discount, 2)
            updated_item['pendingAfTaxDiscountAmount'] = round(af_tax_discount, 2)
            updated_item['pendingCgst'] = round(pending_cgst, 2)
            updated_item['pendingSgst'] = round(pending_sgst, 2)
            updated_item['pendingIgst'] = round(pending_igst, 2)
            updated_item['pendingTaxAmount'] = round(item_pending_tax, 2)

            updated_item['finalPrice'] = item_final_price
            updated_item['pendingFinalPrice'] = item_pending_final_price

            # Append updated item
            updated_items.append({
                "itemId": item_patch['itemId'],
                "quantity": updated_item['quantity'],
                "count": updated_item['count'],
                "eachQuantity": updated_item['eachQuantity'],
                "pendingCount": updated_item['pendingCount'],
                "newPrice": updated_item['newPrice'],
                "pendingQuantity": updated_item['pendingQuantity'],
                "taxPercentage": updated_item['taxPercentage'],
                "befTaxDiscount": updated_item['befTaxDiscount'],
                "afTaxDiscount": updated_item['afTaxDiscount'],
                "pendingTotalQuantity": pending_total_quantity,
                "receivedQuantity": total_quantity,
                "damagedQuantity": damaged_quantity,
                "status": updated_item['status']
            })

            if updated_item['pendingCount'] > 0:
                all_items_received = False

    # Calculate final totals including all items
    total_discount += item_discount
    total_amount_after_discount = total_amount_before_tax - total_discount
    final_total_after_tax = total_amount_after_discount + total_tax
    totalOrderAmount = round(final_total_after_tax, 2)

    total_pending_discount += item_pending_discount
    total_amount_pending_after_discount = total_amount_pending_before_tax - total_pending_discount
    final_total_pending_after_tax = total_amount_pending_after_discount + total_pending_tax
    pendingOrderAmount = round(final_total_pending_after_tax, 2)

    # Set item status based on whether all items are received
    item_status = "ItemReceived" if all_items_received else "Pending"

    # Update purchase order in the database
    get_purchaseorder_collection().update_one(
        {"_id": ObjectId(purchaseOrderId)},
        {"$set": {
            "totalOrderAmount": totalOrderAmount,
            "pendingOrderAmount": pendingOrderAmount,
            "pendingDiscountAmount": total_pending_discount,
            "pendingTaxAmount": total_pending_tax,
            "discountPrice": item_discount,
            "totalDiscount": total_discount,
            "totalTax": total_tax,
            "itemStatus": item_status,
            "invoiceNo": purchaseOrderPatch['invoiceNo'],
            "invoiceDate": purchaseOrderPatch['invoiceDate'],
            "items": existing_purchaseorder['items']
        }}
    )

    # Return response with updated totals and item details
    return {
        "totalOrderAmount": totalOrderAmount,
        "totalDiscount": round(total_discount, 2),
        "totalAmountBeforeTax": round(total_amount_before_tax, 2),
        "totalTax": round(total_tax, 2),
        "invoiceNo": purchaseOrderPatch['invoiceNo'],
        "invoiceDate": purchaseOrderPatch["invoiceDate"],
        "itemStatus": item_status,
        "itemDetails": updated_items
    }
