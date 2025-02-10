from typing import List
from fastapi import APIRouter, HTTPException,status
from bson import ObjectId
from .models import Category, CategoryPost
from .utils import get_category_collection

router = APIRouter()

purchase_category_counter = 0

def get_next_counter_value():
    counter_collection = get_category_collection().database["counters"]
    counter = counter_collection.find_one_and_update(
        {"_id": "categoryId"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

def reset_counter():
    counter_collection = get_category_collection().database["counters"]
    counter_collection.update_one(
        
        {"_id": "categoryId"},
        {"$set": {"sequence_value": 0}},
        upsert=True
    )

def generate_random_id():
    counter_value = get_next_counter_value()
    return f"IC{counter_value:03d}"

@router.post("/", response_model=str,status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryPost):
    # Ensure subCategory is a list
    if category.subCategory is None:
        category.subCategory = []

    # Check if the collection is empty
    if get_category_collection().count_documents({}) == 0:
        reset_counter()

    # Generate randomId
    random_id = generate_random_id()

    # Prepare data including randomId
    new_category_data = category.dict()
    new_category_data['randomId'] = random_id

    # Insert into MongoDB
    result = get_category_collection().insert_one(new_category_data)
    return str(result.inserted_id)

@router.get("/", response_model=List[Category])
async def get_all_category():
    categories = list(get_category_collection().find())
    formatted_categories = []
    for cat in categories:
        cat["categoryId"] = str(cat["_id"])
        if isinstance(cat.get("subCategory"), str):
            cat["subCategory"] = [cat["subCategory"]]  # Convert string to list
        elif cat.get("subCategory") is None:
            cat["subCategory"] = []  # Ensure it's a list
        formatted_categories.append(Category(**cat))
    return formatted_categories

@router.get("/{category_id}", response_model=Category)
async def get_category_by_id(category_id: str):
    category = get_category_collection().find_one({"_id": ObjectId(category_id)})
    if category:
        category["categoryId"] = str(category["_id"])
        if isinstance(category.get("subCategory"), str):
            category["subCategory"] = [category["subCategory"]]  # Convert string to list
        elif category.get("subCategory") is None:
            category["subCategory"] = []  # Ensure it's a list
        return Category(**category)
    else:
        raise HTTPException(status_code=404, detail="category not found")

@router.put("/{category_id}")
async def update_category(category_id: str, category: CategoryPost):
    # Ensure subCategory is a list
    if category.subCategory is None:
        category.subCategory = []

    updated_category = category.dict(exclude_unset=True)
    result = get_category_collection().update_one({"_id": ObjectId(category_id)}, {"$set": updated_category})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="category not found")
    return {"message": "category updated successfully"}

@router.patch("/{category_id}")
async def patch_category(category_id: str, category_patch: CategoryPost):
    existing_category = get_category_collection().find_one({"_id": ObjectId(category_id)})
    if not existing_category:
        raise HTTPException(status_code=404, detail="category not found")

    # Ensure subCategory is a list
    if category_patch.subCategory is None:
        category_patch.subCategory = []

    updated_fields = {key: value for key, value in category_patch.dict(exclude_unset=True).items() if value is not None}
    if updated_fields:
        result = get_category_collection().update_one({"_id": ObjectId(category_id)}, {"$set": updated_fields})
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update category")

    updated_category = get_category_collection().find_one({"_id": ObjectId(category_id)})
    updated_category["_id"] = str(updated_category["_id"])
    if isinstance(updated_category.get("subCategory"), str):
        updated_category["subCategory"] = [updated_category["subCategory"]]  # Convert string to list
    elif updated_category.get("subCategory") is None:
        updated_category["subCategory"] = []  # Ensure it's a list
    return updated_category

@router.delete("/{category_id}")
async def delete_category(category_id: str):
    result = get_category_collection().delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="category not found")
    return {"message": "category deleted successfully"}
