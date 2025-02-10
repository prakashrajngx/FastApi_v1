import io
import os
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
import requests  # Correct import for handling HTTP requests
from fastapi.responses import JSONResponse, StreamingResponse
from pymongo.errors import DuplicateKeyError
from PIL import Image
from ftplib import FTP, error_perm
from .utils import get_webpromoslider_collection

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/promocard"
BASE_URL = "https://yenerp.com/share/upload/promocard"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# MongoDB Collection
photos_collection = get_webpromoslider_collection()

# Initialize router
router = APIRouter()

def compress_image(image_bytes: bytes, max_size: int = 800) -> bytes:
    """Compresses and resizes an image before uploading."""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    width, height = image.size
    if width > max_size or height > max_size:
        image.thumbnail((max_size, max_size))
    compressed_io = io.BytesIO()
    image.save(compressed_io, format="WebP", quality=70)
    return compressed_io.getvalue()

async def upload_to_ftp(file_path: str, remote_filename: str) -> str:
    """Uploads a file to the FTP server and returns its URL."""
    try:
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)
        folders = FTP_UPLOAD_DIR.strip("/").split("/")
        for folder in folders:
            try:
                ftp.cwd(folder)
            except error_perm:
                ftp.mkd(folder)
                ftp.cwd(folder)
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)
        ftp.quit()
        return f"{BASE_URL}/{remote_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...), paragraph: Optional[str] = None, photo_id: Optional[str] = Query(default=None)):
    """Upload a promo card image, compress it, store it on FTP, and save metadata in MongoDB."""
    try:
        contents = await file.read()
        compressed_contents = compress_image(contents)
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, file.filename)
        with open(temp_path, "wb") as f:
            f.write(compressed_contents)
        if not photo_id:
            photo_id = get_next_custom_id()
        ftp_url = await upload_to_ftp(temp_path, f"{photo_id}.webp")
        os.remove(temp_path)
        document = {"_id": photo_id, "filename": file.filename, "url": ftp_url, "paragraph": paragraph}
        photos_collection.insert_one(document)
        return {"filename": file.filename, "id": photo_id, "url": ftp_url, "paragraph": paragraph}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail=f"Photo with ID '{photo_id}' already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view/{photo_id}")
async def get_photo(photo_id: str):
    """Retrieve and display the promo card image by ID."""
    try:
        # Fetch the document from MongoDB
        photo_document = photos_collection.find_one({"_id": photo_id})
        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        # Get image URL from the document
        image_url = photo_document["url"]

        # Fetch the image using requests
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return StreamingResponse(response.raw, media_type="image/webp")

        raise HTTPException(status_code=500, detail="Failed to fetch image from FTP server")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/popupad/{photo_id}")
async def get_popup_ad(photo_id: str):
    """
    Retrieve the popup ad image and associated paragraph by its ID.
    """
    try:
        photo_document = photos_collection.find_one({"_id": photo_id})

        if photo_document:
            content = photo_document["content"]
            paragraph = photo_document.get("paragraph", "No description available.")
            return {
                "image": StreamingResponse(io.BytesIO(content), media_type="image/jpeg"),
                "paragraph": paragraph
            }
        else:
            raise HTTPException(status_code=404, detail="Popup ad not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/category/view/{photo_id}")
async def update_photo(
    photo_id: str,
    file: Optional[UploadFile] = File(None),
    paragraph: Optional[str] = Query(None)
):
    """
    Update a photo's file or paragraph.
    The new image is compressed before updating.
    """
    try:
        update_fields = {}
        if file:
            contents = await file.read()
            compressed_contents = compress_image(contents)
            update_fields["filename"] = file.filename
            update_fields["content"] = compressed_contents
        if paragraph:
            update_fields["paragraph"] = paragraph

        if not update_fields:
            raise HTTPException(status_code=400, detail="No updates provided.")

        result = photos_collection.update_one({"_id": photo_id}, {"$set": update_fields})
        if result.matched_count == 1:
            return {"message": "Photo updated successfully"}
        raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/view/{photo_id}")
async def delete_photo(photo_id: str):
    """
    Delete a photo by its ID.
    """
    try:
        # Delete the document from MongoDB
        result = photos_collection.delete_one({"_id": photo_id})

        if result.deleted_count == 1:
            return {"message": "Photo deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/view")
async def get_all_photos():
    """
    Retrieve all photos with their metadata.
    """
    try:
        # Fetch all photos from the collection
        photos_cursor = photos_collection.find()

        # Convert the cursor to a list and format the result
        photos_list = [
            {
                "id": str(photo["_id"]),  # Convert ObjectId to string
                "filename": photo["filename"],
                "paragraph": photo.get("paragraph", None)
            }
            for photo in photos_cursor
        ]

        return {"photos": photos_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_next_custom_id():
    """Generate the next custom ID (e.g., 's1', 's2')."""
    last_doc = photos_collection.find_one({"_id": {"$regex": "^s[0-9]+$"}}, sort=[("_id", -1)])
    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"s{next_id_num}"
    return "s1"

