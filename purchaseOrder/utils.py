from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
db = client["reactfluttertest"]  # Adjust database name as per your MongoDB setup
# MongoDB connection and collection getter for item groups
def get_purchaseorder_collection():
    return db['purchaseorder']  

def get_image_collection():
    return db['Imageforpurchase']