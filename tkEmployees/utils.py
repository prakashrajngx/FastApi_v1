from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection and collection getter for items
def get_employee_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["ticketManagement"]
    return db['employee']

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
import re
from pymongo.collection import Collection

# Utility function to generate a sequential employee ID
def generate_custom_emp_id(employee_collection: Collection) -> str:
    # Fetch the latest empId
    latest_employee = employee_collection.find_one(sort=[("empId", -1)])
    if latest_employee and "empId" in latest_employee:
        match = re.match(r'^ITC(\d+)$', latest_employee["empId"])
        if match:
            current_max_id = int(match[1])
        else:
            current_max_id = 0
    else:
        current_max_id = 0

    new_emp_id = f'ITC{current_max_id + 1:03}'
    return new_emp_id
