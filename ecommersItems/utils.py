from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection and collection getter for item groups
def get_item_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["reactfluttertest"]  # Adjust database name as per your MongoDB setup
    return db['webitems']  



client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")  # Use your MongoDB connection URI
db = client['reactfluttertest']  # Replace with your actual database name

# Function to get the image collection
def get_webimage_collection():
    return db['webitemsimages']  # The name of your new image collection


client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")  # Use your MongoDB connection URI
db = client['reactfluttertest']  # Replace with your actual database name

# Function to get the image collection
def get_webimage2_collection():
    return db['webitemsimages2']  # The name of your new image collection