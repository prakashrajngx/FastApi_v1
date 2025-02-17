from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pymongo import MongoClient
from ftplib import FTP, error_perm
from webofferslider.utils import get_webofferslider_collection
import io
from bson import ObjectId
from PIL import Image
import os
import uuid

# 🔹 FTP Credentials
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/offerslider"
BASE_URL = "https://yenerp.com/share/upload"

# 🔹 Local temporary storage
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# 🔹 MongoDB connection
client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
db = client["reactfluttertest"]
banner_collection = db["bannersphoto"]

router = APIRouter()

# 🔹 Image Compression Function
def compress_image(image_bytes: bytes, max_size: int = 800) -> bytes:
    """Compresses an image, resizes it, and converts to WebP format."""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")  # Convert to RGB for compatibility

    # Resize if necessary
    width, height = image.size
    if width > max_size or height > max_size:
        image.thumbnail((max_size, max_size))

    # Convert to WebP and compress
    compressed_io = io.BytesIO()
    image.save(compressed_io, format="WebP", quality=70)  # WebP for better compression
    return compressed_io.getvalue()

# 🔹 FTP Upload Function
def upload_to_ftp(file_path: str, remote_filename: str) -> str:
    """Uploads a file to the FTP server and returns the URL."""
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

        return f"{BASE_URL}/{remote_filename}"  # Return accessible image URL
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

# 🔹 Upload Photo Endpoint
@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    try:
        # Read and compress image
        contents = await file.read()
        compressed_contents = compress_image(contents)

        # Save locally before FTP upload
        temp_filename = f"{uuid.uuid4().hex}.webp"
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, temp_filename)
        with open(temp_path, "wb") as f:
            f.write(compressed_contents)

        # Upload to FTP
        image_url = upload_to_ftp(temp_path, temp_filename)

        # Store image URL in MongoDB
        result = banner_collection.insert_one({
            "filename": file.filename,
            "url": image_url
        })

        return {"custom_id": str(result.inserted_id), "url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Get All Photos Endpoint
@router.get("/all")
async def get_all_photos():
    try:
        banners = banner_collection.find({}, {"_id": 1, "filename": 1, "url": 1})
        images = [{"custom_id": str(banner["_id"]), "filename": banner["filename"], "url": banner["url"]} for banner in banners]
        if not images:
            raise HTTPException(status_code=404, detail="No images found")
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/view/{custom_id}")
async def get_photo(custom_id: str):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        image_url = banner["url"]
        filename = image_url.split("/")[-1]  # Extract the filename from URL

        # Connect to FTP and download the image
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_UPLOAD_DIR)

        image_io = io.BytesIO()
        ftp.retrbinary(f"RETR {filename}", image_io.write)
        ftp.quit()

        image_io.seek(0)
        return StreamingResponse(image_io, media_type="image/webp")  # Adjust format as needed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 Delete Photo Endpoint
@router.delete("/delete/{custom_id}")
async def delete_photo(custom_id: str):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        # Get file name from URL
        image_url = banner["url"]
        filename = image_url.split("/")[-1]

        # Remove from FTP
        try:
            ftp = FTP()
            ftp.set_pasv(True)
            ftp.connect(FTP_HOST, 21, timeout=10)
            ftp.login(FTP_USER, FTP_PASSWORD)
            ftp.cwd(FTP_UPLOAD_DIR)
            ftp.delete(filename)
            ftp.quit()
        except Exception as ftp_error:
            raise HTTPException(status_code=500, detail=f"FTP delete failed: {str(ftp_error)}")

        # Remove from MongoDB
        banner_collection.delete_one({"_id": object_id})

        return {"message": "Photo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Update Photo Endpoint
@router.patch("/update/{custom_id}")
async def update_photo(custom_id: str, file: UploadFile = File(...)):
    try:
        object_id = ObjectId(custom_id)
        banner = banner_collection.find_one({"_id": object_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Custom ID not found")

        # Read and compress new image
        contents = await file.read()
        compressed_contents = compress_image(contents)

        # Save locally before FTP upload
        new_filename = f"{uuid.uuid4().hex}.webp"
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, new_filename)
        with open(temp_path, "wb") as f:
            f.write(compressed_contents)

        # Upload new image to FTP
        new_image_url = upload_to_ftp(temp_path, new_filename)

        # Delete old image from FTP
        old_filename = banner["url"].split("/")[-1]
        try:
            ftp = FTP()
            ftp.set_pasv(True)
            ftp.connect(FTP_HOST, 21, timeout=10)
            ftp.login(FTP_USER, FTP_PASSWORD)
            ftp.cwd(FTP_UPLOAD_DIR)
            ftp.delete(old_filename)
            ftp.quit()
        except Exception as ftp_error:
            raise HTTPException(status_code=500, detail=f"Failed to delete old FTP image: {str(ftp_error)}")

        # Update document in MongoDB
        banner_collection.update_one(
            {"_id": object_id},
            {"$set": {"filename": file.filename, "url": new_image_url}}
        )

        return {"message": "Photo updated successfully", "new_url": new_image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
