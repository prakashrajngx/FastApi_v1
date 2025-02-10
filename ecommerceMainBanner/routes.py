from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from bson import ObjectId
import io

# MongoDB connection
client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
db = client["reactfluttertest"]
banner_collection = db["webMainBanner"]

router = APIRouter()

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...), custom_id: str = None):
    try:
        if not custom_id:
            raise HTTPException(status_code=400, detail="Custom ID is required.")

        contents = await file.read()

        banner_collection.insert_one({
            "_id": custom_id,
            "filename": file.filename,
            "content": contents,
        })

        return {"id": custom_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_photos():
    try:
        photos = banner_collection.find()
        result = [{"id": photo["_id"], "filename": photo["filename"]} for photo in photos]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{photo_id}")
async def get_photo(photo_id: str):
    try:
        photo = banner_collection.find_one({"_id": photo_id})
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")

        return StreamingResponse(io.BytesIO(photo["content"]), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/update/{photo_id}")
async def update_photo(photo_id: str, file: UploadFile = File(...)):
    try:
        contents = await file.read()

        result = banner_collection.update_one(
            {"_id": photo_id},
            {"$set": {"filename": file.filename, "content": contents}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Photo not found")

        return {"message": "Photo updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{photo_id}")
async def delete_photo(photo_id: str):
    try:
        result = banner_collection.delete_one({"_id": photo_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Photo not found")

        return {"message": "Photo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
