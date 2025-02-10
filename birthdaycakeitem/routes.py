import io
import logging
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from bson import ObjectId
from typing import List
from .models import BirthdayCakeItem, BirthdayCakeItemPost, Variant
from .utils import get_BirthdayCakeItem_collection, get_BirthdayCakeItem_collection, convert_to_string_or_emptys, get_BirthdayCakeItem_collection
import os

router = APIRouter()

@router.post("/", response_model=str)
async def create_BirthdayCakeItem(BirthdayCakeItem: BirthdayCakeItemPost):
    new_BirthdayCakeItem = BirthdayCakeItem.dict()  # Convert Pydantic model to dictionary
    result = get_BirthdayCakeItem_collection().insert_one(new_BirthdayCakeItem)
    return str(result.inserted_id)


@router.get("/")
async def get_all_BirthdayCakeItems():
    BirthdayCakeItems = list(get_BirthdayCakeItem_collection().find())
    for item in BirthdayCakeItems:
        item["birthdayCakeId"] = str(item.pop("_id"))  # Use parentheses for pop
        
    return BirthdayCakeItems


@router.get("/{birthdayCakeId}", response_model=BirthdayCakeItem)
async def get_BirthdayCakeItem_by_id(birthdayCakeId: str):
    BirthdayCakeItem = get_BirthdayCakeItem_collection().find_one({"_id": ObjectId(birthdayCakeId)})
    if BirthdayCakeItem:
        BirthdayCakeItem["_id"] = str(BirthdayCakeItem["_id"])
        BirthdayCakeItem["birthdayCakeId"] = BirthdayCakeItem["_id"]
        return BirthdayCakeItem(**convert_to_string_or_emptys(BirthdayCakeItem))
    else:
        raise HTTPException(status_code=404, detail="BirthdayCakeItem not found")

@router.put("/{birthdayCakeId}")
async def update_BirthdayCakeItem(birthdayCakeId: str, BirthdayCakeItem: BirthdayCakeItemPost):
    updated_fields = BirthdayCakeItem.dict(exclude_unset=True)
    result = get_BirthdayCakeItem_collection().update_one(
        {"_id": ObjectId(birthdayCakeId)},
        {"$set": convert_to_string_or_emptys(updated_fields)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="BirthdayCakeItem not found")
    return {"message": "BirthdayCakeItem updated successfully"}

@router.delete("/{birthdayCakeId}")
async def delete_BirthdayCakeItem(birthdayCakeId: str):
    result = get_BirthdayCakeItem_collection().delete_one({"_id": ObjectId(birthdayCakeId)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="BirthdayCakeItem not found")
    return {"message": "BirthdayCakeItem deleted successfully"}

@router.patch("/{birthdayCakeId}/deactivate")
async def deactivate_BirthdayCakeItem(birthdayCakeId: str):
    try:
        obj_id = ObjectId(birthdayCakeId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid birthdayCakeId format: {birthdayCakeId}") from e
    
    result = get_BirthdayCakeItem_collection().update_one(
        {"_id": obj_id},
        {"$set": {"status": "inactive"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"BirthdayCakeItem with ID {birthdayCakeId} not found")
    return {"message": "BirthdayCakeItem deactivated successfully"}

@router.patch("/{birthdayCakeId}/activate")
async def activate_BirthdayCakeItem(birthdayCakeId: str):
    try:
        obj_id = ObjectId(birthdayCakeId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid birthdayCakeId format: {birthdayCakeId}") from e
    
    result = get_BirthdayCakeItem_collection().update_one(
        {"_id": obj_id},
        {"$set": {"status": "active"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"BirthdayCakeItem with ID {birthdayCakeId} not found")
    return {"message": "BirthdayCakeItem activated successfully"}

# Import API
@router.post("/import")
async def import_excel(file: UploadFile):
    try:
        # Read the uploaded file
        contents = await file.read()
        filename = file.filename.lower()

        # Detect file type
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel file.")

        # Column name mapping (CSV to expected API fields)
        column_mapping = {
            "name": "itemName",
            "kg": "Kg",
            "tax": "taxPercentage",
            "hsnCode": "hsCode",
            "stockQuantity": "availableStock"
        }

        # Rename the columns to match required ones
        df.rename(columns=column_mapping, inplace=True)

        # Drop unnecessary columns if needed
        unnecessary_columns = {"itemCode", "butterscotchflavour", "chocolateflavour"}
        df.drop(columns=[col for col in unnecessary_columns if col in df.columns], inplace=True)

        # Validate required columns
        required_columns = {
            "category", "subCategory", "itemName", "Kg", "variant", "taxPercentage",
            "netPrice", "finalPrice", "uom", "hsCode", "status", "type", "availableStock"
        }

        if not required_columns.issubset(set(df.columns)):
            missing_columns = required_columns - set(df.columns)
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_columns)}")

        # Replace empty fields with None
        df = df.where(pd.notnull(df), None)

        # Process each row and insert into the collection
        items = df.to_dict(orient="records")

        # Insert data into MongoDB collection
        collection = get_BirthdayCakeItem_collection()
        result = collection.insert_many(items)

        # Return success message
        return {
            "message": "File imported and data inserted successfully",
            "inserted_count": len(result.inserted_ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
