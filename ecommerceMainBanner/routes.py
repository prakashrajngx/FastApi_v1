import os
import io
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pymongo import MongoClient
from PIL import Image
from ftplib import FTP, error_perm
import requests

# 🔹 FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/logo"
BASE_URL = "https://yenerp.com/share/upload"

# 🔹 Local temporary storage
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

# 🔹 MongoDB connection
client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
db = client["reactfluttertest"]
banner_collection = db["webMainBanner"]

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

        return f"{BASE_URL}/ecommerce/logo/{remote_filename}"  # Return accessible image URL
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

# 🔹 Upload Image Route
@router.post("/upload")
async def upload_photo(file: UploadFile = File(...), custom_id: str = None):
    if not custom_id:
        raise HTTPException(status_code=400, detail="Custom ID is required.")

    try:
        # 🔸 Compress image
        compressed_image = compress_image(await file.read())

        # 🔸 Save temporarily
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{custom_id}.webp")
        with open(temp_path, "wb") as temp_file:
            temp_file.write(compressed_image)

        # 🔸 Upload to FTP
        ftp_url = upload_to_ftp(temp_path, f"{custom_id}.webp")

        # 🔸 Store metadata in MongoDB
        banner_collection.insert_one({
            "_id": custom_id,
            "filename": f"{custom_id}.webp",
            "url": ftp_url
        })

        return JSONResponse(content={"id": custom_id, "filename": file.filename, "url": ftp_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Get Image URL by ID

@router.get("/view/{photo_id}")
async def get_photo(photo_id: str):
    """Fetches and streams the image directly from the FTP URL."""
    photo = banner_collection.find_one({"_id": photo_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    image_url = photo["url"]
    
    # 🔹 Fetch the image from FTP URL
    response = requests.get(image_url, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch image from FTP")
    
    # 🔹 Stream the image response
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type="image/webp")

# 🔹 List All Images
@router.get("/list")
async def list_photos():
    """Returns all stored images with their URLs."""
    photos = banner_collection.find()
    result = [{"id": photo["_id"], "filename": photo["filename"], "url": photo["url"]} for photo in photos]
    return result

# 🔹 Update Image (Replace Old Image with New One)
@router.patch("/update/{photo_id}")
async def update_photo(photo_id: str, file: UploadFile = File(...)):
    try:
        photo = banner_collection.find_one({"_id": photo_id})
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")

        # 🔸 Compress new image
        compressed_image = compress_image(await file.read())

        # 🔸 Save temporarily
        temp_path = os.path.join(LOCAL_UPLOAD_FOLDER, f"{photo_id}.webp")
        with open(temp_path, "wb") as temp_file:
            temp_file.write(compressed_image)

        # 🔸 Upload new image to FTP
        new_ftp_url = upload_to_ftp(temp_path, f"{photo_id}.webp")

        # 🔸 Update MongoDB
        banner_collection.update_one(
            {"_id": photo_id},
            {"$set": {"filename": f"{photo_id}.webp", "url": new_ftp_url}}
        )

        return {"message": "Photo updated successfully", "url": new_ftp_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Delete Image
@router.delete("/delete/{photo_id}")
async def delete_photo(photo_id: str):
    """Deletes an image from MongoDB and the FTP server."""
    photo = banner_collection.find_one({"_id": photo_id})
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Change to directory and delete file
        ftp.cwd(FTP_UPLOAD_DIR)
        ftp.delete(f"{photo_id}.webp")
        ftp.quit()

        # Remove from MongoDB
        banner_collection.delete_one({"_id": photo_id})

        return {"message": "Photo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete photo: {str(e)}")
