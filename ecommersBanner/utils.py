import os
import re
import uuid
import shutil
import aiofiles
import logging
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from ftplib import FTP, error_perm
from fastapi import HTTPException
from PIL import Image

# Load environment variables
load_dotenv()

# MongoDB connection
def get_WebAdbanner_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["reactfluttertest"]  # Adjust database name if needed
    return db['WebAdbanner']  

# FTP Config
FTP_HOST = "194.233.78.90"
FTP_USER = "yenerp.com_thys677l7kc"
FTP_PASSWORD = "PUTndhivxi6x94^%"
FTP_UPLOAD_DIR = "/httpdocs/share/upload/ecommerce/adbanner"
BASE_URL = "https://yenerp.com/share/upload"

# Temporary local upload folder
LOCAL_UPLOAD_FOLDER = "./temp_uploads"
os.makedirs(LOCAL_UPLOAD_FOLDER, exist_ok=True)

async def upload_to_ftp(file_path: str, remote_filename: str):
    """Uploads a file to the FTP server."""
    try:
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, 21, timeout=10)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Ensure the directory exists
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
        return f"{BASE_URL}/ecommerce/adbanner/{remote_filename}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP upload failed: {str(e)}")

def compress_image(input_path: str, output_path: str, quality: int = 50):
    """Compresses an image and saves it."""
    try:
        img = Image.open(input_path)
        img = img.convert("RGB")  # Ensure compatibility
        img.save(output_path, "JPEG", optimize=True, quality=quality)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")

def get_next_custom_id():
    """Generate the next custom ID for banners."""
    collection = get_WebAdbanner_collection()
    last_doc = collection.find_one(
        {"_id": {"$regex": "^b[0-9]+$"}},
        sort=[("_id", -1)]
    )

    if last_doc:
        last_id = last_doc["_id"]
        next_id_num = int(re.search(r'\d+', last_id).group()) + 1
        return f"b{next_id_num}"
    return "b1"
