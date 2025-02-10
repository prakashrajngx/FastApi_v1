import os
import io
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from pymongo.errors import DuplicateKeyError
from PIL import Image
from ftplib import FTP, error_perm
from .utils import get_webcategory_collection

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/categories"
BASE_URL = "https://yenerp.com/share/upload"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# MongoDB Collection
photos_collection = get_webcategory_collection()

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
        return f"{BASE_URL}/{remote_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")


def get_next_custom_id():
    """Generate the next custom ID."""
    last_doc = photos_collection.find_one(
        {"_id": {"$regex": "^c[0-9]+$"}},
        sort=[("_id", -1)]
    )
    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"c{next_id_num}"
    return "c1"


@router.post("/category/upload")
async def upload_photo(
    file: UploadFile = File(...),
    category_name: Optional[str] = None,
    photo_id: Optional[str] = Query(default=None)
):
    """Upload, compress, and store an image on FTP for fast website display."""
    try:
        contents = await file.read()
        compressed_contents = compress_image(contents)

        if not photo_id:
            photo_id = get_next_custom_id()

        local_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{photo_id}.webp")
        with open(local_path, "wb") as f:
            f.write(compressed_contents)

        ftp_url = await upload_to_ftp(local_path, f"{photo_id}.webp")

        document = {"_id": photo_id, "filename": file.filename, "category_name": category_name, "ftp_url": ftp_url}
        photos_collection.insert_one(document)
        os.remove(local_path)  # Clean up local file

        return {"filename": file.filename, "id": photo_id, "category_name": category_name, "ftp_url": ftp_url}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail=f"Photo with ID '{photo_id}' already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/view/{photo_id}")
async def get_photo(photo_id: str):
    """Retrieve and return a compressed image from FTP for fast website loading."""
    try:
        photo_document = photos_collection.find_one({"_id": photo_id})
        if not photo_document:
            raise HTTPException(status_code=404, detail="Photo not found")

        ftp_url = photo_document["ftp_url"]
        filename = ftp_url.split("/")[-1]  # Extract the filename from the URL

        # Connect to FTP and retrieve the image
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_UPLOAD_DIR)

        image_io = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", image_io.write)
        ftp.quit()

        image_io.seek(0)  # Reset pointer to the beginning
        return StreamingResponse(image_io, media_type="image/webp", headers={"Cache-Control": "max-age=31536000"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/category/view/{photo_id}")
async def update_photo(
    photo_id: str,
    file: Optional[UploadFile] = File(None),
    category_name: Optional[str] = Query(None)
):
    """
    Update a photo's file or category name.
    """
    try:
        update_fields = {}
        if file:
            contents = await file.read()
            update_fields["filename"] = file.filename
            update_fields["content"] = contents
        if category_name:
            update_fields["category_name"] = category_name

        if not update_fields:
            raise HTTPException(status_code=400, detail="No updates provided.")

        # Update the document in MongoDB        
        result = photos_collection.update_one(
            {"_id": photo_id},
            {"$set": update_fields}
        )

        if result.matched_count == 1:
            return {"message": "Photo updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/category/view/{photo_id}")
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


@router.get("/category/view")
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
                "category_name": photo.get("category_name", None)
                
            }
            for photo in photos_cursor
        ]

        return {"photos": photos_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/category/data/view/{photo_id}")
async def get_photo_metadata(photo_id: str):
    """
    Retrieve the category name and other metadata of the photo by its ID.
    """
    try:
        photo_document = photos_collection.find_one({"_id": photo_id})

        if photo_document:
            metadata = {
                "id": str(photo_document["_id"]),
                "category_name": photo_document.get("category_name", "Unknown Category")
            }
            return {"metadata": metadata}
        else:
            raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/names")
async def get_category_names():
    """
    Retrieve a list of all unique category names.
    """
    try:
        # Fetch distinct category names from the photos collection
        category_names = photos_collection.distinct("category_name")
        return {"categoryIds": category_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





def get_next_custom_id():
    """
    Generate the next custom ID in the format 'c1', 'c2', 'c3', etc.        
    """
    last_doc = photos_collection.find_one(
        {"_id": {"$regex": "^c[0-9]+$"}},  # Match custom IDs like "c1", "c2", etc.
        sort=[("_id", -1)]  # Sort by ID in descending order
    )

    if last_doc:
        # Extract the number part of the last custom ID and increment it
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"c{next_id_num}"
    else:
        # If no custom IDs exist, start with "c1"
        return "c1"
