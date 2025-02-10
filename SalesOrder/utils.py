from pymongo import MongoClient
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection and collection getter for item groups
def get_salesOrder_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["reactfluttertest"]  # Adjust database name as per your MongoDB setup
    return db['salesOrder']  

def get_invoice_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client['reactfluttertest']  # Invoice database
    return db
def get_invoice_collection():
    db = get_invoice_database()
    return db['invoice']