from pymongo import MongoClient
import re
from datetime import datetime

# MongoDB connection and collection getter for tickets
def get_ticket_collection():
    client = MongoClient("mongodb://admin:YenE580nOOUE6cDhQERP@194.233.78.90:27017/admin?appName=mongosh+2.1.1&authSource=admin&authMechanism=SCRAM-SHA-256&replicaSet=yenerp-cluster")
    db = client["ticketManagement"]
    return db['tickets']

# Utility function to convert data to strings or empty strings and handle `_id` field
def convert_to_string_or_emptys(data):
    if isinstance(data, list):
        return [convert_to_string_or_emptys(value) for value in data]
    elif isinstance(data, dict):
        # Convert MongoDB's `_id` to `ticketId`
        if '_id' in data:
            data['ticketId'] = str(data.pop('_id'))
        return {key: convert_to_string_or_emptys(value) for key, value in data.items()}
    elif isinstance(data, (int, float)):
        return str(data)
    else:
        return str(data) if data is not None and data != "" else None

# Utility function to generate a sequential ticket ID with format '01ICTddmmyy'
def generate_next_ticket_number(tickets_collection) -> str:
    # Get the current date in DDMMYY format
    current_date = datetime.now().strftime('%d%m%y')
    
    # Regex to find numbers in the '01ICTddmmyy' format where X is a number
    pattern = re.compile(r'^(\d{2})ICT' + current_date + r'$')

    # Fetch all tickets with the current date and extract their numbers to determine the maximum
    tickets = tickets_collection.find({"ticketNo": {"$regex": pattern}})
    max_number = 0

    # Calculate the highest number from existing tickets for the current date
    for ticket in tickets:
        match = pattern.search(ticket["ticketNo"])
        if match:
            ticket_number = int(match.group(1))
            if ticket_number > max_number:
                max_number = ticket_number

    # Generate the new ticket number with incremented sequence
    new_ticket_number = f'{max_number + 1:02}ICT{current_date}'
    return new_ticket_number

# Example usage
tickets_collection = get_ticket_collection()
new_ticket_number = generate_next_ticket_number(tickets_collection)
print(f'New ticket number: {new_ticket_number}')
