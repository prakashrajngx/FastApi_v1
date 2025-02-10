import os
import io
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError
from PIL import Image
from ftplib import FTP
from .utils import get_WebAdbanner_collection
import requests
from fastapi.responses import StreamingResponse

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/adbanner"
BASE_URL = "https://yenerp.com/share/upload"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# MongoDB Collection
webadbanner_collection = get_WebAdbanner_collection()

# Initialize router
router = APIRouter()


def compress_image(image_bytes: bytes, max_size: int = 800) -> bytes:
    """Compresses an image, resizes it, and converts to WebP format."""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")


async def upload_to_ftp(file_path: str, remote_filename: str) -> str:
    """Uploads a file to the FTP server and returns its URL."""
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
            except Exception:
                ftp.mkd(folder)
                ftp.cwd(folder)

        # Upload file
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)
        ftp.quit()

        return f"{BASE_URL}/ecommerce/adbanner/{remote_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")


@router.post("/banner/upload")
async def upload_photo(
    file: UploadFile = File(...),
    photo_id: Optional[str] = None
):
    """Upload and compress a photo before storing its FTP path in MongoDB."""
    try:
        contents = await file.read()

        # Compress Image
        compressed_content = compress_image(contents, max_size=800)

        # Generate unique ID if not provided
        if not photo_id:
            photo_id = get_next_custom_id()

        # Save compressed image temporarily
        file_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{photo_id}.webp")
        with open(file_path, "wb") as f:
            f.write(compressed_content)

        # Upload to FTP
        ftp_url = await upload_to_ftp(file_path, f"{photo_id}.webp")

        # Store in MongoDB
        document = {
            "_id": photo_id,
            "filename": file.filename,
            "url": ftp_url,
        }
        webadbanner_collection.insert_one(document)

        # Remove local temp file
        os.remove(file_path)

        return {"filename": file.filename, "id": photo_id, "url": ftp_url}

    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Photo with ID '{photo_id}' already exists. Please use a unique ID."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/banner/view/{photo_id}")
async def get_photo(photo_id: str):
    """Retrieve an optimized photo by its ID from FTP and serve it directly."""
    try:
        photo_document = webadbanner_collection.find_one({"_id": photo_id})

        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        ftp_url = photo_document["url"]

        # Fetch the image from the FTP URL
        response = requests.get(ftp_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch image from FTP")

        # Return the image as a streaming response
        return StreamingResponse(io.BytesIO(response.content), media_type="image/webp")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/banner/view/{photo_id}")
async def update_photo(
    photo_id: str,
    file: Optional[UploadFile] = File(None),
):
    """Update a photo's file on FTP and in MongoDB."""
    try:
        photo_document = webadbanner_collection.find_one({"_id": photo_id})

        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        update_fields = {}
        if file:
            contents = await file.read()
            compressed_content = compress_image(contents, max_size=800)

            # Save to local temp
            file_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{photo_id}.webp")
            with open(file_path, "wb") as f:
                f.write(compressed_content)

            # Upload to FTP
            ftp_url = await upload_to_ftp(file_path, f"{photo_id}.webp")

            update_fields["filename"] = file.filename
            update_fields["url"] = ftp_url

            # Remove local temp file
            os.remove(file_path)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No updates provided.")

        # Update MongoDB
        result = webadbanner_collection.update_one(
            {"_id": photo_id},
            {"$set": update_fields}
        )

        if result.matched_count == 1:
            return {"message": "Photo updated successfully", "url": ftp_url}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/banner/view/{photo_id}")
async def delete_photo(photo_id: str):
    """Delete a photo from FTP and MongoDB."""
    try:
        photo_document = webadbanner_collection.find_one({"_id": photo_id})

        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        # Delete from MongoDB
        webadbanner_collection.delete_one({"_id": photo_id})

        return {"message": "Photo deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/banner/view")
async def get_all_photos():
    """Retrieve all stored photo URLs."""
    try:
        photos_cursor = webadbanner_collection.find()
        photos_list = [{"id": str(photo["_id"]), "filename": photo["filename"], "url": photo["url"]} for photo in photos_cursor]
        return {"photos": photos_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_next_custom_id():
    """Generate a custom ID in format 'b1', 'b2', etc."""
    last_doc = webadbanner_collection.find_one(
        {"_id": {"$regex": "^b[0-9]+$"}},
        sort=[("_id", -1)]
    )

    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"b{next_id_num}"
    else:
        return "b1"
