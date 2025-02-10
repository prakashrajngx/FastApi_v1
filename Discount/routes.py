from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from .models import discount, discountPost
from .utils import get_discount_collection, convert_to_string_or_none
from fastapi import APIRouter, status

router = APIRouter()

def get_next_counter_value():
    counter_collection = get_discount_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "discountId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_discount_collection().database["counters"]
    counter_collection.update_one(
        {"_id": "discountId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IT{counter_value:03d}"

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_discount(discount: discountPost):
    # Check if the collection is empty
    if get_discount_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_discount_data = discount.dict()
    new_discount_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_discount_collection().insert_one(new_discount_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[discount])
async def get_all_discount():
    try:
        itemdiscount = list(get_discount_collection().find())
        formatted_discount = []
        for discounts in itemdiscount:
            for key, value in discounts.items():
                discounts[key] = convert_to_string_or_none(value)
            discounts["discountId"] = str(discounts["_id"])
            formatted_discount.append(discount(**discounts))
        return formatted_discount
    except Exception as e:
        print(f"Error fetching discounts: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{discount_id}", response_model=discount)
async def get_discount_by_id(discount_id: str):
    try:
        discount_data = get_discount_collection().find_one({"_id": ObjectId(discount_id)})
        if discount_data:
            discount_data["discountId"] = str(discount_data["_id"])
            return discount(**discount_data)
        else:
            raise HTTPException(status_code=404, detail="discount not found")
    except Exception as e:
        print(f"Error fetching discount by ID: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{discount_id}")
async def update_discount(discount_id: str, discount: discountPost):
    updated_discount = discount.dict(exclude_unset=True)  # exclude_unset=True prevents sending None values to MongoDB
    result = get_discount_collection().update_one({"_id": ObjectId(discount_id)}, {"$set": updated_discount})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="discount not found")
    return {"message": "discount updated successfully"}

@router.patch("/{discount_id}")
async def patch_discount(discount_id: str, discount_patch: discountPost):
    existing_discount = get_discount_collection().find_one({"_id": ObjectId(discount_id)})
    if not existing_discount:
        raise HTTPException(status_code=404, detail="discount not found")

    updated_fields = {key: value for key, value in discount_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_discount_collection().update_one({"_id": ObjectId(discount_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update discount")

    updated_discount = get_discount_collection().find_one({"_id": ObjectId(discount_id)})
    updated_discount["_id"] = str(updated_discount["_id"])
    return updated_discount

@router.delete("/{discount_id}")
async def delete_discount(discount_id: str):
    result = get_discount_collection().delete_one({"_id": ObjectId(discount_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="discount not found")
    return {"message": "discount deleted successfully"}
