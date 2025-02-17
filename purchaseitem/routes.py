from datetime import datetime
import io
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from bson import ObjectId
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pytz
from .models import (
    PurchaseItem,
    PurchaseItemPost,
)  # Adjust paths as per your project structure
from .utils import (
    get_purchaseitem_collection,
)  # Adjust import as per your project structure
import csv
import logging

router = APIRouter()


class PaginatedPurchaseItemsResponse(BaseModel):
    items: List[PurchaseItem]  # List of PurchaseItem objects
    totalItems: int  # Total count of items
    currentPage: int  # Current page number
    pageSize: int  # Page size


# Function to get the current date and time with timezone as a datetime object
def get_current_date_and_time(timezone: str = "Asia/Kolkata") -> datetime:
    try:
        # Set the specified timezone
        specified_timezone = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    # Get the current time in the specified timezone and make it timezone-aware
    now = datetime.now(specified_timezone)

    return {"datetime": now}  # Return the ISO 8601 formatted datetime string


def get_next_counter_value():
    counter_collection = get_purchaseitem_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "purchaseitemId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True,
    )
    return counter["sequence_value"]


def reset_counter():
    counter_collection = get_purchaseitem_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "purchaseitemId"}, {"$set": {"sequence_value": 0}}, upsert=True
    )


def generate_random_id():
    counter_value = get_next_counter_value()
    return f"PI{counter_value:03d}"


@router.post("/", response_model=str)
async def create_purchaseitem(purchaseitem_data: PurchaseItemPost):
    try:
        if get_purchaseitem_collection().count_documents({}) == 0:
            reset_counter()

        # Generate a random ID
        random_id = generate_random_id()
        current_date_and_time = get_current_date_and_time()

        # Prepare data including randomId
        new_purchaseitem_data = purchaseitem_data.dict()
        new_purchaseitem_data["randomId"] = random_id
        new_purchaseitem_data["createdDate"] = current_date_and_time[
            "datetime"
        ]  # Add created date

        result = get_purchaseitem_collection().insert_one(new_purchaseitem_data)
        if result.inserted_id:
            return str(result.inserted_id)
        else:
            raise HTTPException(
                status_code=500, detail="Failed to insert purchase item"
            )

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/search", response_model=List[PurchaseItem])
async def search_items(itemName: Optional[str] = None):
    try:
        query = {}

        if itemName:
            query["itemName"] = {
                "$regex": itemName,
                "$options": "i",
            }  # Case-insensitive search

        cursor = get_purchaseitem_collection().find(query)
        purchaseitems = list(cursor)

        formatted_items = []
        for item in purchaseitems:
            item["purchaseitemId"] = str(item["_id"])
            item["purchasePrice"] = item["purchasePrice"]
            item["purchasetaxName"] = item["purchasetaxName"]
            # Ensure that item contains all required fields
            formatted_items.append(PurchaseItem(**item))

        return formatted_items

    except Exception as e:
        logging.error(f"Error occurred while fetching purchase items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/export_csv", response_model=dict, operation_id="export_purchase_items_to_csv"
)
async def export_all_purchase_items_to_csv():
    try:
        # Fetch all purchase items from the MongoDB collection without pagination
        purchaseitems = list(get_purchaseitem_collection().find())

        # If no items found, raise an exception
        if not purchaseitems:
            raise HTTPException(status_code=404, detail="No purchase items found")

        # Create an in-memory stream for the CSV
        csv_stream = io.StringIO()
        csv_writer = csv.writer(csv_stream)

        # Define CSV headers based on your data structure
        headers = [
            "itemName",
            "purchasecategoryName",
            "purchasesubcategoryName",
            "itemgroupName",
            "uom",
            "stockQuantity",
            "supplier",
            "purchasePrice",
            "purchasetaxName",
            "reorderLevel",
            "itemType",
            "hsnCode",
            "shelfLife",
            "vendorTag",
            "locationName",
            "barcode",
            "description",
            "createdDate",
            "lastUpdatedDate",
            "status",
        ]
        csv_writer.writerow(headers)

        # Write each purchase item row to the CSV
        for item in purchaseitems:
            # Convert ObjectId to string and handle missing fields
            row = [
                item.get("itemName", ""),
                item.get("purchasecategoryName", ""),
                item.get("purchasesubcategoryName", ""),
                item.get("itemgroupName", ""),
                item.get("uom", ""),
                item.get("stockQuantity", ""),
                item.get("supplier", ""),
                item.get("purchasePrice", ""),
                item.get("purchasetaxName", ""),
                item.get("reorderLevel", ""),
                item.get("itemType", ""),
                item.get("hsnCode", ""),
                item.get("shelfLife", ""),
                ",".join(item.get("vendorTag", [])),  # Convert list to string
                item.get("locationName", ""),
                item.get("barcode", ""),
                item.get("description", ""),
                item.get("createdDate", ""),
                item.get("lastUpdatedDate", ""),
                item.get("status", ""),
            ]
            csv_writer.writerow(row)

        # Move the stream position to the start
        csv_stream.seek(0)

        # Create a StreamingResponse to return the CSV data as a file download
        response = StreamingResponse(
            iter([csv_stream.getvalue()]), media_type="text/csv"
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=purchase_items.csv"
        )

        return response

    except Exception as e:
        logging.error(f"Error occurred during CSV export: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=Dict)
async def get_all_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=5000),
    itemName: Optional[str] = Query(None),
    purchasecategoryName: Optional[str] = Query(None),
    purchasesubcategoryName: Optional[str] = Query(None),
):
    try:
        query = {}

        # Apply filters if provided
        if itemName:
            query["itemName"] = {"$regex": itemName, "$options": "i"}
        if purchasecategoryName:
            query["purchasecategoryName"] = {
                "$regex": purchasecategoryName,
                "$options": "i",
            }
        if purchasesubcategoryName:
            query["purchasesubcategoryName"] = {
                "$regex": purchasesubcategoryName,
                "$options": "i",
            }

        # Get total count before pagination
        total_count = get_purchaseitem_collection().count_documents(query)

        # Get paginated data
        cursor = get_purchaseitem_collection().find(query).skip(skip).limit(limit)
        purchaseitems = list(cursor)

        # Format the fetched data
        formatted_items = []
        for item in purchaseitems:
            item["purchaseitemId"] = str(item["_id"])
            formatted_items.append(PurchaseItem(**item))

        return {"items": formatted_items, "totalItems": total_count}

    except Exception as e:
        logging.error(f"Error occurred while fetching purchase items: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/{purchaseitem_id}", response_model=PurchaseItem)
async def get_purchaseitem_by_id(purchaseitem_id: str):
    purchaseitem = get_purchaseitem_collection().find_one(
        {"_id": ObjectId(purchaseitem_id)}
    )
    if purchaseitem:
        return PurchaseItem(**purchaseitem)
    else:
        raise HTTPException(status_code=404, detail="PurchaseItem not found")


@router.put("/{purchaseitem_id}")
async def update_purchaseitem(
    purchaseitem_id: str, purchaseitem_data: PurchaseItemPost
):
    try:
        updated_purchaseitem = purchaseitem_data.dict(
            exclude_unset=True
        )  # exclude_unset=True prevents sending None values to MongoDB
        current_date_and_time = get_current_date_and_time()
        updated_purchaseitem["lastUpdatedDate"] = current_date_and_time["datetime"]

        result = get_purchaseitem_collection().replace_one(
            {"_id": ObjectId(purchaseitem_id)}, updated_purchaseitem
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="PurchaseItem not found")

        return {"message": "PurchaseItem updated successfully"}

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/{purchaseitem_id}")
async def patch_purchaseitem(
    purchaseitem_id: str, purchaseitem_patch: PurchaseItemPost
):
    try:
        existing_purchaseitem = get_purchaseitem_collection().find_one(
            {"_id": ObjectId(purchaseitem_id)}
        )
        if not existing_purchaseitem:
            raise HTTPException(status_code=404, detail="PurchaseItem not found")

        updated_fields = purchaseitem_patch.dict(exclude_unset=True)

        if updated_fields:
            updated_fields["lastUpdatedDate"] = get_current_date_and_time()["datetime"]
            result = get_purchaseitem_collection().update_one(
                {"_id": ObjectId(purchaseitem_id)}, {"$set": updated_fields}
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=500, detail="Failed to update PurchaseItem"
                )

        updated_purchaseitem = get_purchaseitem_collection().find_one(
            {"_id": ObjectId(purchaseitem_id)}
        )
        return PurchaseItem(**updated_purchaseitem)

    except Exception as e:
        logging.error(f"Error occurred while patching PurchaseItem: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{purchaseitem_id}")
async def delete_purchaseitem(purchaseitem_id: str):
    result = get_purchaseitem_collection().delete_one(
        {"_id": ObjectId(purchaseitem_id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="PurchaseItem not found")

    return {"message": "PurchaseItem deleted successfully"}


@router.post("/import_csv", response_model=dict)
async def import_purchase_items_from_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = contents.decode("utf-8").splitlines()
        csv_reader = csv.DictReader(data)

        headers = csv_reader.fieldnames
        if not headers:
            raise HTTPException(status_code=400, detail="Invalid CSV file format")

        purchase_items = []

        # Query to get the current highest randomId from the database
        last_item = get_purchaseitem_collection().find_one(sort=[("randomId", -1)])
        last_random_id = 0
        current_date = get_current_date_and_time()["datetime"]
        item_status = "active"

        if last_item and last_item.get("randomId"):
            try:
                last_random_id = int(
                    last_item["randomId"][2:]
                )  # Extract the numeric part of the last randomId
            except ValueError:
                last_random_id = 0

        for idx, row in enumerate(csv_reader):
            for key in ["stockQuantity", "purchasePrice", "reorderLevel"]:
                if row.get(key):
                    row[key] = row[key].replace(",", "")

            # Generate new randomId in the format PI001, PI002, etc.
            new_random_id = f"PI{last_random_id + idx + 1:03d}"

            purchase_item_data = {
                "itemName": row.get("itemName"),
                "purchasecategoryName": row.get("purchasecategoryName"),
                "purchasesubcategoryName": row.get("purchasesubcategoryName"),
                "itemgroupName": row.get("itemgroupName"),
                "uom": row.get("uom"),
                "stockQuantity": (
                    float(row["stockQuantity"]) if row.get("stockQuantity") else None
                ),
                "supplier": row.get("supplier"),
                "purchasePrice": (
                    float(row["purchasePrice"]) if row.get("purchasePrice") else None
                ),
                "purchasetaxName": row.get("purchasetaxName"),
                "reorderLevel": (
                    int(row["reorderLevel"]) if row.get("reorderLevel") else None
                ),
                "itemType": row.get("itemType"),
                "hsnCode": row.get("hsnCode"),
                "shelfLife": row.get("shelfLife"),
                "vendorTag": (
                    row.get("vendorTag").split(",") if row.get("vendorTag") else []
                ),
                "locationName": row.get("locationName"),
                "barcode": row.get("barcode"),
                "description": row.get("description"),
                "createdDate": current_date,
                "lastUpdatedDate": current_date,
                "status": item_status,
                "randomId": new_random_id,  # Assigning the generated randomId
            }

            purchase_items.append(purchase_item_data)

        if purchase_items:
            get_purchaseitem_collection().insert_many(purchase_items)

        return {"message": f"{len(purchase_items)} items imported successfully"}

    except Exception as e:
        logging.error(f"Error occurred during CSV import: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/export_csv", response_model=dict)
async def export_all_purchase_items_to_csv():
    try:
        # Fetch all purchase items from the MongoDB collection without pagination
        purchaseitems = list(get_purchaseitem_collection().find())

        # If no items found, raise an exception
        if not purchaseitems:
            raise HTTPException(status_code=404, detail="No purchase items found")

        # Create an in-memory stream for the CSV
        csv_stream = io.StringIO()
        csv_writer = csv.writer(csv_stream)

        # Define CSV headers based on your data structure
        headers = [
            "itemName",
            "purchasecategoryName",
            "purchasesubcategoryName",
            "itemgroupName",
            "uom",
            "stockQuantity",
            "supplier",
            "purchasePrice",
            "purchasetaxName",
            "reorderLevel",
            "itemType",
            "hsnCode",
            "shelfLife",
            "vendorTag",
            "locationName",
            "barcode",
            "description",
            "createdDate",
            "lastUpdatedDate",
            "status",
        ]
        csv_writer.writerow(headers)

        # Write each purchase item row to the CSV
        for item in purchaseitems:
            # Convert ObjectId to string and handle missing fields
            row = [
                item.get("itemName", ""),
                item.get("purchasecategoryName", ""),
                item.get("purchasesubcategoryName", ""),
                item.get("itemgroupName", ""),
                item.get("uom", ""),
                item.get("stockQuantity", ""),
                item.get("supplier", ""),
                item.get("purchasePrice", ""),
                item.get("purchasetaxName", ""),
                item.get("reorderLevel", ""),
                item.get("itemType", ""),
                item.get("hsnCode", ""),
                item.get("shelfLife", ""),
                ",".join(item.get("vendorTag", [])),  # Convert list to string
                item.get("locationName", ""),
                item.get("barcode", ""),
                item.get("description", ""),
                item.get("createdDate", ""),
                item.get("lastUpdatedDate", ""),
                item.get("status", ""),
            ]
            csv_writer.writerow(row)

        # Move the stream position to the start
        csv_stream.seek(0)

        # Create a StreamingResponse to return the CSV data as a file download
        response = StreamingResponse(
            iter([csv_stream.getvalue()]), media_type="text/csv"
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=purchase_items.csv"
        )

        return response

    except Exception as e:
        logging.error(f"Error occurred during CSV export: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
