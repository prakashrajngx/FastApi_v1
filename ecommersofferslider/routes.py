# from fastapi import APIRouter, HTTPException, UploadFile, File
# from fastapi.responses import StreamingResponse
# from pymongo import MongoClient
# from ecommersofferslider.utils import get_webofferslider_collection
# import io
# from bson import ObjectId  # Import for handling ObjectId

# # MongoDB collection
# banner_collection = get_webofferslider_collection()

# router = APIRouter()

# # Route for uploading a single image (MongoDB will generate _id)
# @router.post("/upload")
# async def upload_photo(file: UploadFile = File(...)):
#     try:
#         # Read the file
#         contents = await file.read()

#         # Insert a new document with auto-generated _id
#         result = banner_collection.insert_one({
#             "filename": file.filename,
#             "content": contents
#         })

#         return {"custom_id": str(result.inserted_id), "file": file.filename}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Route to view a specific photo by its custom ID
# @router.get("/view/{custom_id}")
# async def get_photo(custom_id: str):
#     try:
#         # Convert custom_id (string) to ObjectId
#         object_id = ObjectId(custom_id)
        
#         # Find the document with the given custom ID
#         banner = banner_collection.find_one({"_id": object_id})
        
#         if not banner:
#             raise HTTPException(status_code=404, detail="Custom ID not found")
        
#         # Return the photo content as a StreamingResponse
#         return StreamingResponse(io.BytesIO(banner["content"]), media_type="image/jpeg")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Route to update a specific photo by its custom ID
# @router.patch("/update/{custom_id}")
# async def update_photo(custom_id: str, file: UploadFile = File(...)):
#     try:
#         # Convert custom_id (string) to ObjectId
#         object_id = ObjectId(custom_id)
        
#         # Find the document with the given custom ID
#         banner = banner_collection.find_one({"_id": object_id})
        
#         if not banner:
#             raise HTTPException(status_code=404, detail="Custom ID not found")

#         # Read the new content for the photo
#         contents = await file.read()

#         # Update the document with the new photo content
#         banner_collection.update_one(
#             {"_id": object_id},
#             {"$set": {"filename": file.filename, "content": contents}}
#         )

#         return {"message": "Photo updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Route to delete a specific photo by its custom ID
# @router.delete("/delete/{custom_id}")
# async def delete_photo(custom_id: str):
#     try:
#         # Convert custom_id (string) to ObjectId
#         object_id = ObjectId(custom_id)
        
#         # Find the document with the given custom ID
#         banner = banner_collection.find_one({"_id": object_id})
        
#         if not banner:
#             raise HTTPException(status_code=404, detail="Custom ID not found")

#         # Delete the document from the collection
#         banner_collection.delete_one({"_id": object_id})

#         return {"message": "Photo deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Route to get all photos (with custom_id and filename)
# @router.get("/all")
# async def get_all_photos():
#     try:
#         # Fetch all images in the collection, only returning _id and filename fields
#         banners = banner_collection.find({}, {"_id": 1, "filename": 1})
        
#         # Convert MongoDB documents to a list of dicts with custom_id and filename
#         images = [{"custom_id": str(banner["_id"]), "filename": banner["filename"]} for banner in banners]

#         if not images:
#             raise HTTPException(status_code=404, detail="No images found")
        
#         return images
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pymongo import MongoClient
from ecommersofferslider.utils import get_webofferslider_collection, get_public_url
from bson import ObjectId
from PIL import Image
import os
import io

# Define directories
UPLOAD_DIR = "/var/www/vhosts/yenerp.com/httpdocs/share/upload/images"
COMPRESSED_DIR = "/var/www/vhosts/yenerp.com/httpdocs/share/upload/compressed_images"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(COMPRESSED_DIR, exist_ok=True)

# MongoDB collection
banner_collection = get_webofferslider_collection()

# API Router
router = APIRouter()

def compress_image(image_bytes: bytes, output_path: str, quality: int = 50):
    """Compress and save image."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")  # Convert to RGB (removes transparency issues)
        image.save(output_path, "JPEG", quality=quality)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compressing image: {str(e)}")

# Route for uploading and compressing an image
@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    try:
        # Generate file paths
        original_path = os.path.join(UPLOAD_DIR, file.filename)
        compressed_path = os.path.join(COMPRESSED_DIR, file.filename)

        # Read file contents
        contents = await file.read()

        # Compress and save the image
        compress_image(contents, compressed_path, quality=50)

        # Save only the file path in MongoDB
        result = banner_collection.insert_one({
            "filename": file.filename,
            "file_path": compressed_path
        })

        return {
            "custom_id": str(result.inserted_id),
            "file": file.filename,
            "url": get_public_url(compressed_path)  # Generate public URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to view an image
@router.get("/view/{custom_id}")
async def get_photo(custom_id: str):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})

        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        return FileResponse(banner["file_path"], media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to update a specific photo by its custom ID
@router.patch("/update/{custom_id}")
async def update_photo(custom_id: str, file: UploadFile = File(...)):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})

        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        # Generate new file path
        compressed_path = os.path.join(COMPRESSED_DIR, file.filename)

        # Read and compress the new image
        contents = await file.read()
        compress_image(contents, compressed_path, quality=50)

        # Update MongoDB document with new file path
        banner_collection.update_one(
            {"_id": object_id},
            {"$set": {"filename": file.filename, "file_path": compressed_path}}
        )

        return {"message": "Photo updated successfully", "url": get_public_url(compressed_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to delete a specific photo by its custom ID
@router.delete("/delete/{custom_id}")
async def delete_photo(custom_id: str):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})

        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        # Delete the image file from the server
        if os.path.exists(banner["file_path"]):
            os.remove(banner["file_path"])

        # Remove entry from MongoDB
        banner_collection.delete_one({"_id": object_id})

        return {"message": "Photo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to get all photos
@router.get("/all")
async def get_all_photos():
    try:
        banners = banner_collection.find({}, {"_id": 1, "filename": 1, "file_path": 1})

        images = [{
            "custom_id": str(banner["_id"]),
            "filename": banner["filename"],
            "url": get_public_url(banner["file_path"])
        } for banner in banners]

        if not images:
            raise HTTPException(status_code=404, detail="No images found")

        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
