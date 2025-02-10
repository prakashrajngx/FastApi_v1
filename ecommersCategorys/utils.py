import os
import io
import re
from ftplib import FTP, error_perm
from pymongo import MongoClient
from PIL import Image
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables (if needed)
load_dotenv()

# MongoDB Connection
def get_webcategory_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["reactfluttertest"]
    return db["webcategories"]

photos_collection = get_webcategory_collection()

# FTP Configuration
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/webcategories"
BASE_URL = "https://yenerp.com/share/upload"

async def upload_to_ftp(file_path: str, remote_filename: str) -> str:
    """Uploads a file to the FTP server and returns its public URL."""
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
        return f"{BASE_URL}/ecommerce/webcategories/{remote_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

async def compress_and_save_image(file: bytes, filename: str) -> str:
    """Compresses an image, saves it locally, uploads to FTP, and returns the public URL."""
    try:
        image = Image.open(io.BytesIO(file))
        if image.mode != "RGB":
            image = image.convert("RGB")

        temp_path = f"./temp/{filename}"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)

        image.save(temp_path, "JPEG", quality=60, optimize=True)
        public_url = await upload_to_ftp(temp_path, filename)

        os.remove(temp_path)  # Clean up temp file
        return public_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")

def get_next_custom_id() -> str:
    """Generates the next custom ID in the format 'c1', 'c2', 'c3', etc."""
    last_doc = photos_collection.find_one(
        {"_id": {"$regex": "^c[0-9]+$"}},
        sort=[("_id", -1)]
    )
    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r"\d+", last_id).group()) + 1
        return f"c{next_id_num}"
    return "c1"
