from pymongo import MongoClient
from bson import ObjectId

# Global MongoDB client instance
client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")

# Database reference
db = client["reactfluttertest"]  # Adjust database name as per your MongoDB setup

# Function to get the 'businessdetails' collection
def get_businessdetails_collection():
    return db['businessdetails']

# Function to get the 'Imageforpurchase' collection
def get_image_collection():
    return db['Imageforpurchase']