from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File,status
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

# MongoDB connection and collection getter for promotion photos
def get_promotionphoto_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["ticketManagement"]  # Adjust database name as per your MongoDB setup
    return db['ticketreceiptphotos']  # Adjust collection name as per your MongoDB setup

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...), custom_id: Optional[str] = None):
    try:
        # Read the contents of the uploaded file
        contents = await file.read()

        # Check if custom_id is provided, otherwise generate a new ObjectId
        if custom_id:
            custom_object_id = custom_id
        else:
            custom_object_id = str(ObjectId())

        # Insert the file contents into MongoDB with the custom ID
        result = get_promotionphoto_collection().insert_one({
            "_id": custom_object_id,
            "filename": file.filename,
            "content": contents
        })

        return {"filename": file.filename, "id": custom_object_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view/{photo_id}")
async def get_photo(photo_id: str):
    try:
        # Retrieve document from MongoDB
        photo_document = get_promotionphoto_collection().find_one({"_id": photo_id})

        if photo_document:
            # Retrieve content
            content = photo_document["content"]

            # Return StreamingResponse with correct media type
            return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")  # Adjust media_type as per your image format

        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update/{photo_id}")
async def update_photo(photo_id: str, file: UploadFile = File(...)):
    try:
        # Read the contents of the uploaded file
        contents = await file.read()

        # Update the document in MongoDB
        result = get_promotionphoto_collection().update_one(
            {"_id": photo_id},
            {"$set": { 
                "filename": file.filename,
                "content": contents
            }}
        )

        if result.matched_count == 1:
            return {"message": "Photo updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{photo_id}")
async def delete_photo(photo_id: str):
    try:
        # Delete the document from MongoDB
        result = get_promotionphoto_collection().delete_one({"_id": photo_id})

        if result.deleted_count == 1:
            return {"message": "Photo deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))