import io
import ftplib
import logging
import os
from PIL import Image
from typing import List
from fastapi import APIRouter, HTTPException, File, Response, UploadFile
from bson import ObjectId
from fastapi.responses import StreamingResponse
from .models import webitems, webitemspost
from .utils import get_item_collection, get_webimage_collection, get_webimage2_collection

# Get the MongoDB collections
item_collection = get_item_collection()
image_collection = get_webimage_collection()
image_collection2 = get_webimage2_collection()


# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/items"
BASE_URL = "https://yenerp.com/share/upload"

# Local temp folder for processing
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

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

async def upload_to_ftp(file_bytes: bytes, remote_filename: str):
    """Uploads a file to the FTP server."""
    try:
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Ensure directory exists
        folders = FTP_UPLOAD_DIR.strip("/").split("/")
        for folder in folders:
            try:
                ftp.cwd(folder)
            except ftplib.error_perm:
                ftp.mkd(folder)
                ftp.cwd(folder)

        # Upload file using binary mode
        with io.BytesIO(file_bytes) as f:
            ftp.storbinary(f"STOR {remote_filename}", f)

        ftp.quit()
        return f"{BASE_URL}/ecommerce/items/{remote_filename}"
    
    except Exception as e:
        logging.error(f"FTP Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")


# Create API Router
router = APIRouter()
# Route to create a new web item
@router.post("/post", response_model=dict)
async def create_webitem(item: webitemspost):
    try:
        # Convert Pydantic model to dictionary (excluding unset fields)
        new_item = item.dict(exclude_unset=True)

        # Ensure fields are cast to the correct types
        if new_item.get("price"):
            new_item["price"] = float(new_item["price"])
        if new_item.get("strickprice"):
            new_item["strickprice"] = str(new_item["strickprice"])
        if new_item.get("tax"):
            new_item["tax"] = float(new_item["tax"])
        if new_item.get("uom"):
            new_item["uom"] = str(new_item["uom"])
        if new_item.get("gram"):
            new_item["gram"] = str(new_item["gram"])

        # Insert the item into MongoDB
        result = item_collection.insert_one(new_item)

        # Add the inserted ObjectId to the new item and set itemid to the ObjectId
        new_item["_id"] = str(result.inserted_id)
        new_item["itemid"] = new_item["_id"]

        # Return only the itemid in the response
        return {"itemid": new_item["itemid"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting item: {str(e)}")


# Route to get all web items
@router.get("/all", response_model=List[webitems])
async def get_webitems():
    try:
        # Fetch all items from MongoDB
        items = list(item_collection.find())

        # If no items are found, raise a 404 error
        if not items:
            raise HTTPException(status_code=404, detail="No items found")

        # Process each item in the collection
        for item in items:
            item["_id"] = str(item["_id"])

            # Ensure type consistency for fields (e.g., price, tax, uom)
            if isinstance(item.get("price"), str):
                item["price"] = float(item["price"])
            if isinstance(item.get("strickprice"), str):
                item["strickprice"] = float(item["strickprice"])
            if isinstance(item.get("tax"), str):
                item["tax"] = float(item["tax"])
            if isinstance(item.get("uom"), float):
                item["uom"] = str(item["uom"])
            if isinstance(item.get("gram"), float):
                item["gram"] = float(item["gram"])

        return [webitems(**item) for item in items]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


# Route to get a single web item by ID
@router.get("/get/{item_id}", response_model=webitems)
async def get_webitem(item_id: str):
    try:
        # Fetch the item from MongoDB using ObjectId
        item = item_collection.find_one({"_id": ObjectId(item_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item["_id"] = str(item["_id"])
        return webitems(**item)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")


# Route to deactivate a web item by ID
@router.put("/deactivate/{item_id}", response_model=dict)
async def deactivate_webitem(item_id: str):
    try:
        item = item_collection.find_one({"_id": ObjectId(item_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        update_result = item_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {"deactivated": True}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to deactivate item")

        return {"message": "Item successfully deactivated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating item: {str(e)}")


# Route to update a web item by ID
@router.put("/update/{item_id}", response_model=dict)
async def update_webitem(item_id: str, updated_item: webitemspost):
    try:
        # Fetch the item from MongoDB using ObjectId
        item = item_collection.find_one({"_id": ObjectId(item_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Convert the Pydantic model to a dictionary, excluding unset fields
        update_data = updated_item.dict(exclude_unset=True)

        # Ensure fields are cast to the correct types
        if "price" in update_data:
            update_data["price"] = float(update_data["price"])
        if "strickprice" in update_data:
            update_data["strickprice "] = float(update_data["strickprice"])
        if "tax" in update_data:
            update_data["tax"] = float(update_data["tax"])
        if "uom" in update_data:
            update_data["uom"] = str(update_data["uom"])
        if "gram" in update_data:
            update_data["gram"] = str(update_data["gram"])

        # Update the item in MongoDB
        update_result = item_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )

        # Check if the update was successful
        if update_result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update item")

        return {"message": "Item successfully updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")



# Route to delete a web item by ID
@router.delete("/delete/{item_id}", response_model=dict)
async def delete_webitem(item_id: str):
    try:
        item = item_collection.find_one({"_id": ObjectId(item_id)})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        delete_result = item_collection.delete_one({"_id": ObjectId(item_id)})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete item")

        return {"message": "Item successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")


@router.post("/upload_image/{item_id}")
async def upload_image(item_id: str, file: UploadFile = File(...)):
    try:
        # Check if item exists
        item = item_collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Read and compress the uploaded image
        original_content = await file.read()
        compressed_content = compress_image(original_content)

        # Upload to FTP
        ftp_file_path = await upload_to_ftp(compressed_content, f"{item_id}.webp")

        # Store FTP path in MongoDB
        image_collection.insert_one({
            "item_id": ObjectId(item_id),
            "ftp_path": ftp_file_path,
        })

        return {"message": f"Image uploaded successfully for item {item_id}", "ftp_path": ftp_file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")



@router.get("/get_image/{item_id}")
async def get_image(item_id: str):
    try:
        # Validate item_id
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid item_id format")

        # Get image record from MongoDB
        image_record = image_collection.find_one({"item_id": ObjectId(item_id)})
        if not image_record:
            raise HTTPException(status_code=404, detail="Image not found")

        # Get FTP file path
        ftp_path = image_record["ftp_path"]
        filename = ftp_path.split("/")[-1]  # Extract filename from path

        # Connect to FTP
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        # Navigate to directory
        ftp.cwd(FTP_UPLOAD_DIR)

        # Retrieve image as binary
        image_data = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", image_data.write)
        ftp.quit()

        # Get image bytes
        image_data.seek(0)

        # Return the image response
        return Response(content=image_data.read(), media_type="image/jpeg")  # Change MIME type if needed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")

@router.get("/get_all_images", response_model=List[dict])
async def get_all_images():
    try:
        # Fetch all images from the image collection
        images = list(image_collection.find())

        # If no images are found
        if not images:
            raise HTTPException(status_code=404, detail="No images found")

        image_responses = []
        for image in images:
            # Convert ObjectId to string for JSON serialization
            image["_id"] = str(image["_id"])

            image_responses.append({
                "item_id": str(image["item_id"]),
                "image": StreamingResponse(io.BytesIO(image["image"]), media_type="image/jpeg"),
            })

        return image_responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching images: {str(e)}")


@router.put("/edit_image/{item_id}")
async def edit_image(item_id: str, file: UploadFile = File(...)):
    """
    Update or replace an image associated with an item using the item_id.
    """
    try:
        # Fetch the item from the database to ensure it exists
        item = item_collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Read the new image file
        new_image_content = await file.read()

        # Check if an image already exists for the given item_id
        existing_image = image_collection.find_one({"item_id": ObjectId(item_id)})
        if existing_image:
            # Update the existing image in the database
            update_result = image_collection.update_one(
                {"item_id": ObjectId(item_id)},
                {"$set": {"image": new_image_content}}
            )
            if update_result.matched_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update image")
        else:
            # If no image exists, insert a new one
            image_collection.insert_one({
                "item_id": ObjectId(item_id),
                "image": new_image_content,
            })

        return {"message": f"Image successfully updated for item {item_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing image: {str(e)}")



@router.post("/upload_image2/{item_id}")
async def upload_image2(item_id: str, file: UploadFile = File(...)):
    try:
        # Validate if item_id is a proper 24-character hex string
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid item_id format. Must be a 24-character hex string.")

        # Convert to ObjectId
        item_id_obj = ObjectId(item_id)

        item = item_collection.find_one({"_id": item_id_obj})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        original_content = await file.read()
        compressed_content = compress_image(original_content)

        # Fix: Await the async function
        ftp_file_path = await upload_to_ftp(compressed_content, f"{item_id}_2.jpg")

        image_collection2.insert_one({
            "item_id": item_id_obj,
            "ftp_path": ftp_file_path,
        })

        return {"message": f"Image uploaded successfully for item {item_id} in second collection", "ftp_path": ftp_file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image to second collection: {str(e)}")



@router.get("/get_image2/{item_id}")
async def get_image2(item_id: str):
    try:
        # Validate item_id
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid item_id format")

        # Get image record from MongoDB
        image_record = image_collection2.find_one({"item_id": ObjectId(item_id)})
        if not image_record:
            raise HTTPException(status_code=404, detail="Image not found in second collection")

        # Get FTP file path
        ftp_path = image_record.get("ftp_path")
        if not ftp_path:
            raise HTTPException(status_code=404, detail="FTP path not found in record")

        # Extract filename from FTP path
        filename = ftp_path.split("/")[-1]

        # Connect to FTP and retrieve the image
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Navigate to the correct directory
        ftp.cwd(FTP_UPLOAD_DIR)

        # Read the file from FTP
        image_io = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", image_io.write)
        ftp.quit()

        # Return the image as a response
        image_io.seek(0)  # Reset buffer position
        return Response(content=image_io.read(), media_type="image/jpeg")  # Adjust media type if needed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image from FTP: {str(e)}")


# Route to get all images from the second collection
@router.get("/get_all_images2", response_model=List[dict])
async def get_all_images2():
    try:
        # Fetch all images from the second collection
        images = list(image_collection2.find())

        # If no images are found
        if not images:
            raise HTTPException(status_code=404, detail="No images found in the second collection")

        image_responses = []
        for image in images:
            # Convert ObjectId to string for JSON serialization
            image["_id"] = str(image["_id"])

            image_responses.append({
                "item_id": str(image["item_id"]),
                "image": StreamingResponse(io.BytesIO(image["image"]), media_type="image/jpeg"),
            })

        return image_responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching images from second collection: {str(e)}")  

@router.put("/edit_image2/{item_id}")
async def edit_image2(item_id: str, file: UploadFile = File(...)):
    """
    Update or replace an image in the second collection using the item_id.
    """
    try:
        # Check if the item exists in the main collection
        item = item_collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Read the new image file
        new_image_content = await file.read()

        # Check if an image already exists in the second collection for the given item_id
        existing_image = image_collection2.find_one({"item_id": ObjectId(item_id)})
        if existing_image:
            # Update the existing image in the database
            update_result = image_collection2.update_one(
                {"item_id": ObjectId(item_id)},
                {"$set": {"image": new_image_content}}
            )
            if update_result.matched_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update image in the second collection")
        else:
            # If no image exists, insert a new one
            image_collection2.insert_one({
                "item_id": ObjectId(item_id),
                "image": new_image_content,
            })

        return {"message": f"Image successfully updated for item {item_id} in the second collection"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing image in the second collection: {str(e)}")
