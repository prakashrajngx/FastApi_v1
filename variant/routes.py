from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import variant, variantPost
from .utils import get_variant_collection, convert_to_string_or_none

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_variant_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "variantId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_variant_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "variantId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"Var{counter_value:03d}"

@router.post("/", response_model=str)
async def create_variant(variant: variantPost):
    # Check if the collection is empty
    if get_variant_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_variant_data = variant.dict()
    new_variant_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_variant_collection().insert_one(new_variant_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[variant])
async def get_all_variant():
    try:
        itemvariant = list(get_variant_collection().find())
        formatted_variant = []
        for variants in itemvariant:
            variants["_id"] = str(variants["_id"])  # Ensure _id is a string
            for key, value in variants.items():
                variants[key] = convert_to_string_or_none(value)
            variants["variantId"] = variants["_id"]
            formatted_variant.append(variant(**variants))
        return formatted_variant
    except Exception as e:
        print(f"Error fetching variants: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@router.get("/", response_model=List[variant])
async def get_all_variant():
    try:
        itemvariant = list(get_variant_collection().find())
        formatted_variant = []
        for variants in itemvariant:
            variants["_id"] = str(variants["_id"])  # Convert _id to string
            # Ensure all keys are present; provide defaults if needed
            variants["variantItems"] = variants.get("variantItems", [])
            variants["variantId"] = variants["_id"]
            formatted_variant.append(variant(**variants))
        return formatted_variant
    except Exception as e:
        print(f"Error fetching variants: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/{variant_id}")
async def patch_variant(variant_id: str, variant_patch: variantPost):
    if not ObjectId.is_valid(variant_id):
        raise HTTPException(status_code=400, detail="Invalid variantId format")
    
    # Find existing variant
    existing_variant = get_variant_collection().find_one({"_id": ObjectId(variant_id)})
    if not existing_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Prepare updated fields, excluding unset
    updated_fields = {key: value for key, value in variant_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_variant_collection().update_one(
            {"_id": ObjectId(variant_id)},
            {"$set": updated_fields}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update variant")
    else:
        raise HTTPException(status_code=422, detail="No valid fields provided to update")

    # Return updated variant
    updated_variant = get_variant_collection().find_one({"_id": ObjectId(variant_id)})
    updated_variant["_id"] = str(updated_variant["_id"])
    return updated_variant


@router.delete("/{variant_id}")
async def delete_variant(variant_id: str):
    if not ObjectId.is_valid(variant_id):
        raise HTTPException(status_code=400, detail="Invalid variantId format")
    
    result = get_variant_collection().delete_one({"_id": ObjectId(variant_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="variant not found")
    return {"message": "variant deleted successfully"}
