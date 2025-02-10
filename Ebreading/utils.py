


# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo import MongoClient

# MongoDB connection

def ebreading_collection():
  client = MongoClient( "mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
  db = client["dailyactivities"]
  return db['ebReading']  # Adjust this name if necessary
