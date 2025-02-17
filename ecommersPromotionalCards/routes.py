import io
import os
from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile
from bson import ObjectId
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image
from ftplib import FTP
from .models import webpromotionalcard, webpromotionalcardpost
from .utils import get_card_collection, get_image_collection

# Get the MongoDB collections
collection = get_card_collection()
image_collection = get_image_collection()

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/promocard"
BASE_URL = "https://yenerp.com/share/upload"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

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
    """Uploads a file to the FTP server and creates the directory if needed."""
    try:
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Ensure the target directory exists
        directories = FTP_UPLOAD_DIR.strip('/').split('/')
        current_path = ""

        for directory in directories:
            current_path += f"/{directory}"
            try:
                ftp.cwd(current_path)  # Try to enter directory
            except Exception:
                ftp.mkd(current_path)  # Create if doesn't exist
                ftp.cwd(current_path)

        # Open the file and upload it
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)

        ftp.quit()

        return f"{BASE_URL}/ecommerce/promocard/{remote_filename}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

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

        # Read and compress the uploaded file
        file_content = await file.read()
        compressed_image = compress_image(file_content)

        # Create a temporary file
        file_extension = "webp"  # Save as WebP format
        temp_filename = f"{detail_id}.{file_extension}"
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, temp_filename)

        # Save compressed image to temp path
        with open(temp_path, "wb") as temp_file:
            temp_file.write(compressed_image)

        # Upload to FTP
        image_url = await upload_to_ftp(temp_path, temp_filename)

        # Store image URL in MongoDB instead of binary data
        image_document = {
            "detail_id": ObjectId(detail_id),  # Link to the promotional card
            "image_url": image_url  # Store only the image URL
        }
        image_collection.insert_one(image_document)

        # Delete local temp file
        os.remove(temp_path)

        return {"message": "Image uploaded successfully", "image_url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


@router.get("/get_image/{detail_id}")
async def get_image(detail_id: str):
    try:
        # Convert detail_id to ObjectId for MongoDB lookup
        image_item = image_collection.find_one({"detail_id": ObjectId(detail_id)})
        
        if not image_item or "image_url" not in image_item:
            raise HTTPException(status_code=404, detail="Image not found for this item")

        # Extract filename from image URL
        filename = image_item["image_url"].split("/")[-1]
        local_path = os.path.join(LOCAL_UPLOAD_FOLDER, filename)

        # Check if the file exists locally, otherwise download from FTP
        if not os.path.exists(local_path):
            try:
                ftp = FTP()
                ftp.set_pasv(True)
                ftp.connect(FTP_HOST, 21, timeout=10)
                ftp.login(FTP_USER, FTP_PASSWORD)
                ftp.cwd(FTP_UPLOAD_DIR)

                with open(local_path, "wb") as f:
                    ftp.retrbinary(f"RETR " + filename, f.write)

                ftp.quit()
            except Exception as ftp_error:
                raise HTTPException(status_code=500, detail=f"FTP download failed: {str(ftp_error)}")

        # Return the actual image file
        return FileResponse(local_path, media_type="image/webp")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

    

# Route to edit/update an image for a web promotional card
@router.put("/edit_image/{detail_id}")
async def edit_image(detail_id: str, file: UploadFile = File(...)):
    try:
        # Fetch the image document from MongoDB
        image_item = image_collection.find_one({"detail_id": ObjectId(detail_id)})

        if not image_item:
            raise HTTPException(status_code=404, detail="Image not found for this item")

        # Read and compress the new uploaded file
        new_file_content = await file.read()
        compressed_image = compress_image(new_file_content)

        # Create a temporary file
        file_extension = "webp"
        temp_filename = f"{detail_id}.{file_extension}"
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, temp_filename)

        # Save compressed image to temp path
        with open(temp_path, "wb") as temp_file:
            temp_file.write(compressed_image)

        # Upload to FTP
        new_image_url = await upload_to_ftp(temp_path, temp_filename)

        # Update image URL in MongoDB
        update_result = image_collection.update_one(
            {"detail_id": ObjectId(detail_id)},
            {"$set": {"image_url": new_image_url}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update the image")

        # Delete local temp file
        os.remove(temp_path)

        return {"message": "Image successfully updated", "new_image_url": new_image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating image: {str(e)}")