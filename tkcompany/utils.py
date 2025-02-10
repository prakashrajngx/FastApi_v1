from pymongo import MongoClient

# MongoDB connection and collection getter for companies
def get_company_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["ticketManagement"]
    return db['company']

# Utility function to convert data to strings or empty strings
def convert_to_string_or_emptys(data):
    if isinstance(data, list):
        return [convert_to_string_or_emptys(value) for value in data]
    elif isinstance(data, dict):
        return {key: convert_to_string_or_emptys(value) for key, value in data.items()}
    elif isinstance(data, (int, float)):
        return str(data)
    else:
        return str(data) if data is not None and data != "" else None
