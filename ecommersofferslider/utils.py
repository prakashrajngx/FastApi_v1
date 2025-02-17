from pymongo import MongoClient
import os

BASE_URL = "https://yenerp.com/share/upload"
IMAGE_DIR = "/var/www/vhosts/yenerp.com/httpdocs/share/upload/images/offerslider"
COMPRESSED_IMAGE_DIR = "/var/www/vhosts/yenerp.com/httpdocs/share/upload/compressed_images/images/offerslider"

def get_webofferslider_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["reactfluttertest"]  # Adjust database name
    return db['webofferslider']  

def get_public_url(file_path: str) -> str:
    """Convert server file path to public URL."""
    if file_path.startswith(COMPRESSED_IMAGE_DIR):
        relative_path = os.path.relpath(file_path, "/var/www/vhosts/yenerp.com/httpdocs/share/upload")
    else:
        relative_path = os.path.basename(file_path)
    return f"{BASE_URL}/{relative_path}"
