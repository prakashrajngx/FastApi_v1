import io
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from bson import ObjectId
from ngxwebiste_photos.utils import get_ngxphotos_collection

router = APIRouter()

@router.post("/photo/upload")
async def upload_photo(file: UploadFile = File(...), custom_id: Optional[str] = None):
    try:
        contents = await file.read()

        # Use custom_id if provided, otherwise generate a new ObjectId
        custom_object_id = custom_id if custom_id else str(ObjectId())

        # Insert the file contents into MongoDB with the custom ID
        get_ngxphotos_collection().insert_one({
            "_id": custom_object_id,
            "filename": file.filename,
            "content": contents
        })

        return {"filename": file.filename, "id": custom_object_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/photo/view/{photo_id}")
async def get_photo(photo_id: str):
    try:
        photo_document = get_ngxphotos_collection().find_one({"_id": photo_id})

        if photo_document:
            content = photo_document["content"]
            return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")  # Adjust media_type if needed
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/photo/view/{photo_id}")
async def update_photo(photo_id: str, file: UploadFile = File(...)):
    try:
        # Read the contents of the uploaded file
        contents = await file.read()

        # Update the document in MongoDB
        result = get_ngxphotos_collection().update_one(
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
