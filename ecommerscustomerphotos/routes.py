import os
import io
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from pymongo.errors import DuplicateKeyError
from PIL import Image
from ftplib import FTP, error_perm
from .utils import get_webcustomerphotos_collection

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/customer"
BASE_URL = "https://yenerp.com/share/upload"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# MongoDB Collection
photos_collection = get_webcustomerphotos_collection()

# Initialize router
router = APIRouter()


def compress_image(image_bytes: bytes, max_size: int = 800) -> bytes:
    """Compresses an image, resizes it, and converts to WebP format."""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")  # Ensure compatibility

    # Resize if larger than max_size
    width, height = image.size
    if width > max_size or height > max_size:
        image.thumbnail((max_size, max_size))

    # Save as WebP with compression
    compressed_io = io.BytesIO()
    image.save(compressed_io, format="WebP", quality=70)  # WebP for better compression
    return compressed_io.getvalue()


async def upload_to_ftp(file_path: str, remote_filename: str):
    """Uploads a file to the FTP server."""
    try:
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Ensure directory exists
        folders = FTP_UPLOAD_DIR.strip("/").split("/")
        for folder in folders:
            try:
                ftp.cwd(folder)
            except error_perm:
                ftp.mkd(folder)
                ftp.cwd(folder)

        # Upload file
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)
        ftp.quit()
        return f"{BASE_URL}/ecommerce/customer/{remote_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    photo_id: Optional[str] = Query(default=None)
):
    """
    Upload and compress a photo, store it locally, and upload it to FTP.
    """
    try:
        image_bytes = await file.read()
        compressed_content = compress_image(image_bytes)

        # Save compressed image locally
        if not photo_id:
            photo_id = get_next_custom_id()
        local_filename = f"{photo_id}.webp"
        local_path = os.path.join(LOCAL_UPLOAD_FOLDER, local_filename)

        with open(local_path, "wb") as f:
            f.write(compressed_content)

        # Upload to FTP
        ftp_url = await upload_to_ftp(local_path, local_filename)

        # Store in MongoDB
        document = {
            "_id": photo_id,
            "filename": file.filename,
            "ftp_url": ftp_url,
        }
        photos_collection.insert_one(document)

        return {"filename": file.filename, "id": photo_id, "url": ftp_url}

    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail=f"Photo with ID '{photo_id}' already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{photo_id}")
async def get_photo(photo_id: str):
    """
    Retrieve a photo by its ID from MongoDB and return it as a response.
    """
    try:
        # Find the document in MongoDB
        photo_document = photos_collection.find_one({"_id": photo_id})
        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        # Extract the image path from MongoDB
        image_url = photo_document.get("ftp_url")  # Fetch stored FTP/local path
        if not image_url:
            raise HTTPException(status_code=500, detail="Image path not found in database")

        # If stored locally, read from the local path
        local_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{photo_id}.webp")
        if os.path.exists(local_path):  # If stored locally, serve from file
            return StreamingResponse(open(local_path, "rb"), media_type="image/webp")

        # If stored on FTP or external URL, return a redirect response
        return {"image_url": image_url}  # Frontend can use this URL to display the image

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")



@router.delete("/view/{photo_id}")
async def delete_photo(photo_id: str):
    """
    Delete a photo record from MongoDB (does not delete from FTP).
    """
    try:
        result = photos_collection.delete_one({"_id": photo_id})
        if result.deleted_count == 1:
            return {"message": "Photo deleted successfully"}
        raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view")
async def get_all_photos():
    """
    Retrieve all photo metadata.
    """
    try:
        photos_cursor = photos_collection.find()
        photos_list = [{"id": str(photo["_id"]), "filename": photo["filename"], "url": photo["ftp_url"]} for photo in photos_cursor]
        return {"photos": photos_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_next_custom_id():
    """
    Generate the next custom ID in the format 'customer1', 'customer2', etc.
    """
    last_doc = photos_collection.find_one(
        {"_id": {"$regex": "^customer[0-9]+$"}},
        sort=[("_id", -1)]
    )
    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"customer{next_id_num}"
    return "customer1"
