import io
from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile
from bson import ObjectId
from fastapi.responses import StreamingResponse
from .models import webpromotionalcard, webpromotionalcardpost
from .utils import get_card_collection  # Your utility function for MongoDB collection
from .utils import get_image_collection

# Get the MongoDB collection using the utility function
collection = get_card_collection()
image_collection = get_image_collection()


# Create an APIRouter instance
router = APIRouter()

# Route to create a new web promotional card
@router.post("/post", response_model=dict)
async def create_webpromotionalcard(item: webpromotionalcardpost):
    try:
        # Convert Pydantic model to dictionary (excluding unset fields)
        new_item = item.dict(exclude_unset=True)

        # Insert the item into MongoDB
        result = collection.insert_one(new_item)

        # Add the inserted ObjectId to the new item and set itemid to the ObjectId
        new_item["_id"] = str(result.inserted_id)
        new_item["detailid"] = new_item["_id"]

        # Return only the itemid in the response
        return {"detailid": new_item["detailid"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting item: {str(e)}")


# Route to get all web promotional cards
@router.get("/all", response_model=List[webpromotionalcard])
async def get_webpromotionalcards():
    try:
        # Fetch all items from MongoDB
        items = list(collection.find())

        # If no items are found, raise a 404 error
        if not items:
            raise HTTPException(status_code=404, detail="No items found")

        # Process each item in the collection
        for item in items:
            item["_id"] = str(item["_id"])

        return [webpromotionalcard(**item) for item in items]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


# Route to get a single web promotional card by ID
@router.get("/get/{detail_id}", response_model=webpromotionalcard)
async def get_webpromotionalcard(detail_id: str):
    try:
        # Fetch the item from MongoDB using ObjectId
        item = collection.find_one({"_id": ObjectId(detail_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item["_id"] = str(item["_id"])
        return webpromotionalcard(**item)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")
    

    # Route to update the heading and paragraph of a web promotional card
@router.put("/edit/{detail_id}", response_model=dict)
async def edit_webpromotionalcard(detail_id: str, heading: str = None, paragraph: str = None):
    try:
        # Check if the item exists in the collection
        item = collection.find_one({"_id": ObjectId(detail_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Prepare the update document   
        update_fields = {}
        if heading is not None:
            update_fields["heading"] = heading
        if paragraph is not None:
            update_fields["paragraph"] = paragraph

        # Update the item in the collection
        update_result = collection.update_one(
            {"_id": ObjectId(detail_id)},
            {"$set": update_fields}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update item")

        return {"message": "Item successfully updated", "updated_fields": update_fields}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")



# Route to deactivate a web promotional card by ID
@router.put("/deactivate/{detail_id}", response_model=dict)
async def deactivate_webpromotionalcard(detail_id: str):
    try:
        item = collection.find_one({"_id": ObjectId(detail_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        update_result = collection.update_one(
            {"_id": ObjectId(detail_id)},
            {"$set": {"deactivated": True}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to deactivate item")

        return {"message": "Item successfully deactivated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating item: {str(e)}")


# Route to delete a web promotional card by ID
@router.delete("/delete/{detail_id}", response_model=dict)
async def delete_webpromotionalcard(detail_id: str):
    try:
        item = collection.find_one({"_id": ObjectId(detail_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        delete_result = collection.delete_one({"_id": ObjectId(detail_id)})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete item")

        return {"message": "Item successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")


# Route to upload an image for a web promotional card
@router.post("/upload_image/{detail_id}")
async def upload_image(detail_id: str, file: UploadFile = File(...)):
    try:
        # Fetch the item from the promotional card collection
        item = collection.find_one({"_id": ObjectId(detail_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Read the uploaded file
        file_content = await file.read()

        # Store the image in the new image collection
        image_document = {
            "detail_id": ObjectId(detail_id),  # Link to the promotional card
            "image": file_content  # Image content as binary
        }

        # Insert the image document into the image collection
        image_result = image_collection.insert_one(image_document)

        # Return success message
        return {"message": f"Image uploaded successfully for item {detail_id}", "image_id": str(image_result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")



# Route to get an image for a web promotional card
@router.get("/get_image/{detail_id}")
async def get_image(detail_id: str):
    try:
        # Fetch the image document from the image collection
        image_item = image_collection.find_one({"detail_id": ObjectId(detail_id)})

        if not image_item or "image" not in image_item:
            raise HTTPException(status_code=404, detail="Image not found for this item")

        # Get the image content
        image_content = image_item["image"]

        # Return the image as a streaming response
        return StreamingResponse(io.BytesIO(image_content), media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")
    

# Route to edit/update an image for a web promotional card
@router.put("/edit_image/{detail_id}")
async def edit_image(detail_id: str, file: UploadFile = File(...)):
    try:
        # Fetch the image document from the image collection
        image_item = image_collection.find_one({"detail_id": ObjectId(detail_id)})

        if not image_item:
            raise HTTPException(status_code=404, detail="Image not found for this item")

        # Read the new uploaded file
        new_file_content = await file.read()

        # Update the image content in the image collection
        update_result = image_collection.update_one(
            {"detail_id": ObjectId(detail_id)},
            {"$set": {"image": new_file_content}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update the image")

        return {"message": "Image successfully updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating image: {str(e)}")


